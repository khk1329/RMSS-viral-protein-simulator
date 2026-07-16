import csv
import random
from Bio import Align
from Bio import SeqIO
from Bio.Seq import Seq
import os
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import NamedTuple
import matplotlib.pyplot as plt
from functools import lru_cache
import heapq
protein_aligner = Align.PairwiseAligner()
protein_aligner.mode = 'global'

def load_sequence_from_fasta(file_path):
    try:
        with open(file_path, 'r') as handle:
            for record in SeqIO.parse(handle, 'fasta'):
                return str(record.seq)
    except FileNotFoundError:
        print('File not found:', file_path)
        return None

def load_sequences_from_fasta_list(file_paths):
    sequences = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r') as handle:
                for record in SeqIO.parse(handle, 'fasta'):
                    sequences.append((str(record.seq), file_path))
        except FileNotFoundError:
            print('File not found:', file_path)
    return sequences

VALID_DNA_BASES = frozenset('ATGC')
STOP_CODONS = frozenset({'TAA', 'TAG', 'TGA'})
GENERATION_BATCH_SIZE = 1000
SCORE_BATCH_SIZE = 500
CANCEL_CHECK_INTERVAL = 25
WORKER_CACHE_CLEAR_INTERVAL = 100
_worker_last_cache_clear_cycle = 0

class ORFResult(NamedTuple):
    frame: int
    start_nt: int
    stop_nt: int
    cds: str
    protein: str

def normalize_dna(sequence):
    if sequence is None:
        return ''
    return ''.join(str(sequence).split()).upper()

def validate_complete_cds(sequence):
    sequence = normalize_dna(sequence)
    if not sequence:
        return (False, 'Sequence is empty.', None)
    invalid_bases = sorted(set(sequence) - VALID_DNA_BASES)
    if invalid_bases:
        invalid_text = ', '.join(invalid_bases)
        return (False, f'Sequence contains invalid or ambiguous nucleotide(s): {invalid_text}.', None)
    if len(sequence) < 6:
        return (False, 'Sequence is too short to contain a start and stop codon.', None)
    if sequence[:3] != 'ATG':
        return (False, f'Sequence does not start with ATG. Detected first codon: {sequence[:3]}.', None)
    if len(sequence) % 3 != 0:
        return (False, f'Sequence length is not divisible by 3. Length: {len(sequence)} nt.', None)
    terminal_codon = sequence[-3:]
    if terminal_codon not in STOP_CODONS:
        return (False, f'Sequence does not end with a valid stop codon. Detected terminal codon: {terminal_codon}.', None)
    for position in range(3, len(sequence) - 3, 3):
        codon = sequence[position:position + 3]
        if codon in STOP_CODONS:
            codon_number = position // 3 + 1
            return (False, f'Internal in-frame stop codon {codon} was detected at codon {codon_number}.', None)
    return (True, f'Valid complete CDS: {len(sequence)} nt, {len(sequence) // 3 - 1} aa, terminal stop codon {terminal_codon}.', sequence)

def generate_replicate_batch(parent_seq, num_replications, mutation_args, stop_event=None):
    replicated_sequences = replicate_sequence(parent_seq, num_replications, stop_event=stop_event, **mutation_args)
    mutated_sequences = [rep_seq for rep_seq in replicated_sequences if rep_seq != parent_seq]
    unchanged_count = len(replicated_sequences) - len(mutated_sequences)
    return mutated_sequences, unchanged_count, len(replicated_sequences)

def translate_complete_cds(sequence):
    is_valid, _, normalized_sequence = validate_complete_cds(sequence)
    if not is_valid:
        return ''
    coding_region = normalized_sequence[:-3]
    return str(Seq(coding_region).translate(to_stop=False))

@lru_cache(maxsize=200000)
def find_longest_complete_orfs(sequence):
    sequence = normalize_dna(sequence)

    if not sequence or set(sequence) - VALID_DNA_BASES:
        return ()

    selected_orfs = []

    for frame in range(3):
        longest_start = None
        longest_stop = None
        longest_length = -1
        search_position = frame

        while search_position <= len(sequence) - 3:
            start_nt = next(
                (position for position in range(search_position, len(sequence) - 2, 3)
                 if sequence[position:position + 3] == "ATG"),
                None
            )

            if start_nt is None:
                break

            stop_nt = next(
                (position for position in range(start_nt + 3, len(sequence) - 2, 3)
                 if sequence[position:position + 3] in STOP_CODONS),
                None
            )

            if stop_nt is None:
                break

            protein_length = (stop_nt - start_nt) // 3

            if protein_length > longest_length:
                longest_start, longest_stop, longest_length = start_nt, stop_nt, protein_length

            search_position = stop_nt + 3

        if longest_start is not None:
            cds = sequence[longest_start:longest_stop + 3]
            protein = str(Seq(sequence[longest_start:longest_stop]).translate(to_stop=False))
            selected_orfs.append(ORFResult(frame, longest_start, longest_stop, cds, protein))

    return tuple(selected_orfs)

def append_simulation_result_to_csv(file_path, input_seq, final_seq, final_protein):
    input_prot = translate_complete_cds(input_seq)
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(['Input_DNA', 'Best_DNA', 'Input_Protein', 'Best_Protein'])
        writer.writerow([input_seq, final_seq, input_prot, final_protein])

def replicate_sequence(sequence, num_replications, mutation_rate, sub_ratio, indel_ratio, tran_ratio, transv_ratio, stop_event=None):
    replicated_sequences = []
    bases = b'ATCG'
    for replication_index in range(num_replications):
        if replication_index % CANCEL_CHECK_INTERVAL == 0 and stop_event is not None and stop_event.is_set():
            break
        replicated_sequence = bytearray(sequence, 'ascii')
        i = 0
        while i < len(replicated_sequence):
            if random.random() < mutation_rate:
                mut_type = random.choices(['substitution', 'indel'], weights=[sub_ratio, indel_ratio])[0]
                if mut_type == 'substitution':
                    sub_type = random.choices(['transition', 'transversion'], weights=[tran_ratio, transv_ratio])[0]
                    replicated_sequence[i:i + 1] = mutate_base_by_type(replicated_sequence[i:i + 1], sub_type)
                    i += 1
                elif random.random() < 0.5:
                    replicated_sequence.insert(i, random.choice(bases))
                    i += 1
                else:
                    del_len = random.randint(1, min(3, len(replicated_sequence) - i))
                    del replicated_sequence[i:i + del_len]
            else:
                i += 1
        replicated_sequences.append(replicated_sequence.decode('ascii'))
    return replicated_sequences

def mutate_base_by_type(base, mutation_kind):
    base = base.decode('ascii')
    if mutation_kind == 'transition':
        mutated = {'A': 'G', 'G': 'A', 'C': 'T', 'T': 'C'}.get(base, base)
    elif mutation_kind == 'transversion':
        mutated = random.choice({'A': ['C', 'T'], 'G': ['C', 'T'], 'C': ['A', 'G'], 'T': ['A', 'G']}.get(base, [base]))
    else:
        mutated = base
    return mutated.encode('ascii')

def score_replicate(rep, current_inputs, target_protein):
    replicate_orfs = find_longest_complete_orfs(rep)
    if not replicate_orfs:
        return None
    selected_orf = None
    target_score = -1.0
    for orf in replicate_orfs:
        similarity = compare_proteins(orf.protein, target_protein)
        if selected_orf is None:
            selected_orf = orf
            target_score = similarity
            continue
        current_key = (similarity, len(orf.protein), -orf.start_nt)
        selected_key = (target_score, len(selected_orf.protein), -selected_orf.start_nt)
        if current_key > selected_key:
            selected_orf = orf
            target_score = similarity
    return (target_score, None, selected_orf, replicate_orfs)

@lru_cache(maxsize=200000)
def compare_proteins(prot1, prot2):
    if not prot1 or not prot2:
        return 0.0
    if prot1 == prot2:
        return 100.0
    alignment_score = protein_aligner.score(prot1, prot2)
    return alignment_score / max(len(prot1), len(prot2)) * 100

def plot_similarity_graph(cycle_data, result_folder='.'):
    cycles = [c for c, _, _, _, _ in cycle_data]
    target_max = [target_hi for _, target_hi, _, _, _ in cycle_data]
    target_min = [target_lo for _, _, target_lo, _, _ in cycle_data]
    input_max = [input_hi for _, _, _, input_hi, _ in cycle_data]
    input_min = [input_lo for _, _, _, _, input_lo in cycle_data]
    target_err_lower = [target_max[i] - target_min[i] for i in range(len(cycles))]
    input_err_lower = [input_max[i] - input_min[i] for i in range(len(cycles))]
    zero_err = [0] * len(cycles)
    fig, ax = plt.subplots()
    ax.errorbar(cycles, target_max, yerr=[target_err_lower, zero_err], fmt='-', capsize=2, label='Target Similarity (Max/Min)', ecolor='gray')
    ax.errorbar(cycles, input_max, yerr=[input_err_lower, zero_err], fmt='-', capsize=2, label='Input Similarity (Max/Min)', ecolor='gray')
    ax.set_xlabel('Cycle')
    ax.set_ylabel('Similarity (%)')
    ax.set_title('Similarity Trend Across Cycles')
    min_y = min(min(target_min), min(input_min))
    max_y = max(max(target_max), max(input_max))
    margin = 2
    ax.set_ylim(max(0, min_y - margin), min(100, max_y + margin))
    ax.grid(True)
    ax.legend()
    fig.tight_layout()
    save_path = os.path.join(result_folder, 'similarity_trend.png')
    plt.savefig(save_path, dpi=300)
    print(f'Plot saved: {save_path}')
    plt.close(fig)

def score_batch(batch, target_protein, cycle_number, stop_event=None):
    global _worker_last_cache_clear_cycle

    if cycle_number - _worker_last_cache_clear_cycle >= WORKER_CACHE_CLEAR_INTERVAL:
        find_longest_complete_orfs.cache_clear()
        compare_proteins.cache_clear()
        _worker_last_cache_clear_cycle = cycle_number

    batch_results = []

    for result_index, (rep_seq, parent_seq) in enumerate(batch):
        if result_index % CANCEL_CHECK_INTERVAL == 0 and stop_event is not None and stop_event.is_set():
            break

        score_result = score_replicate(rep_seq, None, target_protein)
        batch_results.append((rep_seq, parent_seq, score_result))

    return batch_results
        
def simulate_multiple_cycles(input_sequence, target_sequences, num_cycles, num_replications_per_cycle, mutation_rate, sub_ratio, indel_ratio, tran_ratio, transv_ratio, queue=None, output_folder='.', top_k=1, mutation_rate_str=None, stop_event=None, input_file_name=None, target_file_names=None):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    result_folder = os.path.join(output_folder, timestamp)
    os.makedirs(result_folder, exist_ok=True)

    def log(msg):
        now = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        full_msg = f'{now} {msg}'
        if queue:
            queue.put(('log', full_msg))
        else:
            print(full_msg)
        with open(os.path.join(result_folder, 'simulation_log.txt'), 'a', encoding='utf-8') as f:
            f.write(full_msg + '\n')
            
    input_file_display = input_file_name or 'Unknown'
    target_file_display = ', '.join(target_file_names) if target_file_names else 'Unknown'

    settings_info = f"""
    Simulation started
    ------------------------- Setting Information -------------------------
    ○ Start File: {input_file_display}
    ○ Target File: {target_file_display}
    ○ Mutation Rate: {mutation_rate_str}
    ○ Substitution : INDEL = {sub_ratio} : {indel_ratio}
    ○ Transition : Transversion = {tran_ratio} : {transv_ratio}
    ○ Number of Cycles: {num_cycles}
    ○ Number of Replications per Cycle: {num_replications_per_cycle}
    ○ Top-N selection: {top_k}
    ------------------------------------------------------------------------
    """
    log(settings_info.strip())
    input_valid, input_message, normalized_input = validate_complete_cds(input_sequence)
    if not input_valid:
        log(f'❌ Invalid input CDS: {input_message}')
        if queue:
            queue.put(('done', None))
        return
    if not target_sequences:
        log('❌ No target sequence was provided.')
        if queue:
            queue.put(('done', None))
        return
    target_sequence = target_sequences[0][0]
    target_valid, target_message, normalized_target = validate_complete_cds(target_sequence)
    if not target_valid:
        log(f'❌ Invalid target CDS: {target_message}')
        if queue:
            queue.put(('done', None))
        return
    input_sequence = normalized_input
    target_sequence = normalized_target
    prot_initial = translate_complete_cds(input_sequence)
    target_protein = translate_complete_cds(target_sequence)
    log(f'✅ Input CDS validation passed. {input_message}')
    log(f'✅ Target CDS validation passed. {target_message}')
    mutation_args = {'mutation_rate': mutation_rate, 'sub_ratio': sub_ratio, 'indel_ratio': indel_ratio, 'tran_ratio': tran_ratio, 'transv_ratio': transv_ratio}
    current_input_sequences = [(input_sequence, None)]
    best_similarity = 0
    best_replicate = None
    best_replicate_protein = None
    cycle_data = []
    simulation_status = 'completed'
    cpu_count = os.cpu_count() or 1
    num_workers = max(1, cpu_count - 4)
    with open(os.path.join(result_folder, 'cycle_results.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Cycle', 'InputSequence', 'SelectedSequence', 'InputProteinSimilarity', 'StepwiseProteinSimilarity', 'TargetProteinSimilarity', 'InputProteinSequence', 'SelectedProteinSequence', 'SelectedFrame', 'ORFStartNt', 'ORFStopNt', 'SelectedProteinLengthAA', 'ValidFrameCount'])
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            for cycle in range(num_cycles):
                if stop_event is not None and stop_event.is_set():
                    break
                
                scored = []
                mutated_replicates = []
                parent_score_cache = {}
                unchanged_counts = {}
                generation_futures = {}
                
                for parent_index, (seq, parent_seq) in enumerate(current_input_sequences):
                    if seq not in parent_score_cache:
                        parent_score_cache[seq] = score_replicate(seq, None, target_protein)
                
                    remaining_replications = num_replications_per_cycle
                    generation_batch_index = 0
                
                    while remaining_replications > 0:
                        replication_count = min(GENERATION_BATCH_SIZE, remaining_replications)
                        future = executor.submit(generate_replicate_batch, seq, replication_count, mutation_args, stop_event)
                        generation_futures[future] = (seq, parent_index, generation_batch_index)
                        remaining_replications -= replication_count
                        generation_batch_index += 1
                
                generated_total = 0
                
                for future in as_completed(generation_futures):
                    if stop_event is not None and stop_event.is_set():
                        log('🛑 Stop requested during replicate generation. Aborting generation batches.')
                        for pending_future in generation_futures:
                            pending_future.cancel()
                        break
                
                    try:
                        parent_seq, parent_index, batch_index = generation_futures[future]
                        batch_mutated, unchanged_count, generated_count = future.result()
                        mutated_replicates.extend((rep_seq, parent_seq) for rep_seq in batch_mutated)
                        unchanged_counts[parent_seq] = unchanged_counts.get(parent_seq, 0) + unchanged_count
                        generated_total += generated_count
                
                    except Exception as e:
                        parent_seq, parent_index, batch_index = generation_futures[future]
                        log(f'⚠️ Error in replicate-generation batch {parent_index}-{batch_index}: {e}')
                
                if stop_event is not None and stop_event.is_set():
                    break
                
                for parent_seq, unchanged_count in unchanged_counts.items():
                    parent_score_result = parent_score_cache.get(parent_seq)
                
                    if parent_score_result is None:
                        continue
                
                    target_sim, step_sim, selected_orf, frame_orfs = parent_score_result
                
                    for _ in range(min(unchanged_count, top_k)):
                        scored.append((parent_seq, parent_seq, target_sim, step_sim, selected_orf, frame_orfs))
                
                log(f'[Cycle {cycle + 1}] Mutated replicates: {len(mutated_replicates)}')
                
                score_batches = [mutated_replicates[start_index:start_index + SCORE_BATCH_SIZE] for start_index in range(0, len(mutated_replicates), SCORE_BATCH_SIZE)]
                
                scoring_futures = {executor.submit(score_batch, batch, target_protein, cycle + 1, stop_event): batch_index for batch_index, batch in enumerate(score_batches)}
                                
                for future in as_completed(scoring_futures):
                    if stop_event is not None and stop_event.is_set():
                        log('🛑 Stop requested during scoring. Aborting current cycle.')
                        for pending_future in scoring_futures:
                            pending_future.cancel()
                        break
                
                    try:
                        batch_results = future.result()
                
                        for rep_seq, parent_seq, score_result in batch_results:
                            if score_result is None:
                                continue
                
                            target_sim, step_sim, selected_orf, frame_orfs = score_result
                            scored.append((rep_seq, parent_seq, target_sim, step_sim, selected_orf, frame_orfs))
                
                    except Exception as e:
                        batch_index = scoring_futures[future]
                        log(f'⚠️ Error in scoring batch {batch_index}: {e}')
                
                if stop_event is not None and stop_event.is_set():
                    break
                if not scored:
                    log(f'⚠️ No valid ORF-containing replicates were found in cycle {cycle + 1}.')
                    simulation_status = 'no_scored_results'
                    break
                top = heapq.nlargest(top_k, scored, key=lambda item: item[2])
                current_input_sequences = [(item[0], item[1]) for item in top]
                if (cycle + 1) % 10 == 0:
                    best_rep = max(top, key=lambda item: item[2])
                    rep_seq = best_rep[0]
                    best_sim = best_rep[2]
                    selected_orf = best_rep[4]
                    with open(os.path.join(result_folder, 'best_replicates.fasta'), 'a') as fasta_file:
                        fasta_file.write(f'>Cycle{cycle + 1}_best_replicate_sim{best_sim:.2f}\n')
                        fasta_file.write(rep_seq + '\n\n')
                similarities = [item[2] for item in top]
                if similarities:
                    min_sim = min(similarities)
                    max_sim = max(similarities)
                    log(f'[Cycle {cycle + 1}] Top {top_k} Similarity Range: {min_sim:.2f}% ~ {max_sim:.2f}%')
                for rep, parent, target_sim, step_sim, selected_orf, frame_orfs in top:
                    prot_output = selected_orf.protein
                    parent_orfs = find_longest_complete_orfs(parent) if parent else ()
                    if parent_orfs:
                        parent_orf, step_sim = max(((orf, compare_proteins(prot_output, orf.protein)) for orf in parent_orfs), key=lambda item: item[1])
                        prot_parent = parent_orf.protein
                    else:
                        prot_parent = translate_complete_cds(parent) if parent else prot_initial
                        step_sim = compare_proteins(prot_output, prot_parent)
                    prot_inout = compare_proteins(prot_output, prot_initial)
                    writer.writerow([cycle + 1, parent if parent else rep, rep, f'{prot_inout:.2f}%', f'{step_sim:.2f}%', f'{target_sim:.2f}%', prot_parent, prot_output, selected_orf.frame, selected_orf.start_nt + 1, selected_orf.stop_nt + 3, len(selected_orf.protein), len(frame_orfs)])
                    if target_sim > best_similarity:
                        best_similarity = target_sim
                        best_replicate = rep
                        best_replicate_protein = prot_output
                target_similarities = [target_sim for _, _, target_sim, _, _, _ in top]
                input_similarities = [compare_proteins(selected_orf.protein, prot_initial) for _, _, _, _, selected_orf, _ in top]
                cycle_data.append((cycle + 1, max(target_similarities), min(target_similarities), max(input_similarities), min(input_similarities)))
                log(f'[Cycle {cycle + 1}] ✅ Best similarity so far: {best_similarity:.2f}%')
                mutated_replicates = None
                parent_score_cache = None
                unchanged_counts = None
                generation_futures = None
                score_batches = None
                scoring_futures = None
                scored = None
                if queue:
                    queue.put(('progress', (cycle + 1, num_cycles)))
    if stop_event and stop_event.is_set():
        simulation_status = 'cancelled'
        log('🛑 Simulation was manually stopped.')
    elif simulation_status == 'no_scored_results':
        log('⚠️ Simulation stopped because no valid scored replicates were available.')
    else:
        log('✅ Simulation completed normally.')
    
    if cycle_data:
        try:
            plot_similarity_graph(cycle_data, result_folder)
        except Exception as e:
            log(f'⚠️ Failed to generate similarity graph: {e}')
    if best_replicate and best_replicate_protein:
        try:
            append_simulation_result_to_csv(
                os.path.join(result_folder, 'Final_best_replicate.csv'),
                input_sequence,
                best_replicate,
                best_replicate_protein
            )
            log('Final best replicate saved')
        except Exception as e:
            log(f'⚠️ Failed to save final best replicate: {e}')
    else:
        log('No overall best replicate found.')
    
    if queue:
        queue.put(('done', simulation_status))
