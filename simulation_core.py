import csv
import random
from Bio import Align
from Bio import SeqIO
from Bio.Seq import Seq
import os
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import warnings
import matplotlib.pyplot as plt
from functools import lru_cache
import gc

@lru_cache(maxsize=100000)
def translate_cached(seq):
    return translate_from_start(seq)

translate = translate_cached

protein_aligner = Align.PairwiseAligner()
protein_aligner.mode = 'global'

def load_sequence_from_fasta(file_path):
    try:
        with open(file_path, "r") as handle:
            for record in SeqIO.parse(handle, "fasta"):
                return str(record.seq)
    except FileNotFoundError:
        print("File not found:", file_path)
        return None

def load_sequences_from_fasta_list(file_paths):
    sequences = []
    for file_path in file_paths:
        try:
            with open(file_path, "r") as handle:
                for record in SeqIO.parse(handle, "fasta"):
                    sequences.append((str(record.seq), file_path))
        except FileNotFoundError:
            print("File not found:", file_path)
    return sequences

def append_simulation_result_to_csv(file_path, input_seq, final_seq):
    input_prot = translate(input_seq)
    final_prot = translate(final_seq)
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(["Input_DNA", "Best_DNA", "Input_Protein", "Best_Protein"])
        writer.writerow([input_seq, final_seq, input_prot, final_prot])

def replicate_sequence(sequence, history, num_replications, mutation_rate,
                       sub_ratio, indel_ratio, tran_ratio, transv_ratio):
    replicated_sequences = []
    bases = b"ATCG"

    for _ in range(num_replications):
        replicated_sequence = bytearray(sequence, 'ascii')
        i = 0
        while i < len(replicated_sequence):
            if random.random() < mutation_rate:
                mut_type = random.choices(["substitution", "indel"], weights=[sub_ratio, indel_ratio])[0]
                if mut_type == "substitution":
                    sub_type = random.choices(["transition", "transversion"], weights=[tran_ratio, transv_ratio])[0]
                    replicated_sequence[i:i+1] = mutate_base_by_type(replicated_sequence[i:i+1], sub_type)
                    i += 1
                else:
                    if random.random() < 0.5:
                        replicated_sequence.insert(i, random.choice(bases))
                        i += 1
                    else:
                        del_len = random.randint(1, min(3, len(replicated_sequence) - i))
                        del replicated_sequence[i:i + del_len]
            else:
                i += 1
        new_seq = replicated_sequence.decode('ascii')
        new_history = history.copy()
        new_history.append(new_seq)
        replicated_sequences.append((new_seq, new_history))
    return replicated_sequences

def mutate_base_by_type(base, mutation_kind):
    base = base.decode('ascii')
    if mutation_kind == "transition":
        mutated = {"A": "G", "G": "A", "C": "T", "T": "C"}.get(base, base)
    elif mutation_kind == "transversion":
        mutated = random.choice({"A": ["C", "T"], "G": ["C", "T"], "C": ["A", "G"], "T": ["A", "G"]}.get(base, [base]))
    else:
        mutated = base
    return mutated.encode('ascii')

def replicate_and_score(input_seq, history, num_replications, mutation_args, comparison_proteins, current_inputs):
    replicated_sequences = replicate_sequence(
        input_seq,
        history,
        num_replications,
        mutation_args["mutation_rate"],
        mutation_args["sub_ratio"],
        mutation_args["indel_ratio"],
        mutation_args["tran_ratio"],
        mutation_args["transv_ratio"]
    )
    scored_reps = []
    for rep, hist in replicated_sequences:
        target_score, stepwise_score = score_replicate(rep, current_inputs, comparison_proteins)
        scored_reps.append((rep, hist, target_score, stepwise_score))
    return scored_reps

def score_replicate(rep, current_inputs, target_protein):
    prot_rep = translate(rep)
    best_stepwise = 0
    for seq in current_inputs:
        prot_input = translate(seq)
        score = compare_proteins(prot_rep, prot_input)
        if score > best_stepwise:
            best_stepwise = score
    target_score = compare_proteins(prot_rep, target_protein)
    return target_score, best_stepwise

def find_start_codon(seq):
    return seq.find("ATG")

def translate_from_start(seq):
    start_pos = seq.find("ATG")
    if start_pos == -1:
        warnings.warn("⚠️ No start codon found; using full sequence for translation.")
        coding_region = seq
    else:
        coding_region = seq[start_pos:]

    remainder = len(coding_region) % 3
    if remainder != 0:
        coding_region = coding_region[:-remainder]

    if not coding_region or len(coding_region) < 3:
        warnings.warn("⚠️ Sequence too short to translate.")
        return ""

    try:
        protein = Seq(coding_region).translate(to_stop=False)
        return str(protein)
    except Exception as e:
        warnings.warn(f"⚠️ Translation failed: {e}")
        return ""

@lru_cache(maxsize=100000)
def compare_proteins(prot1, prot2):
    if not prot1 or not prot2:
        return 0.0
    if prot1 == prot2:
        return 100.0
    alignment = protein_aligner.align(prot1, prot2)[0]
    return (alignment.score / max(len(prot1), len(prot2))) * 100

def plot_similarity_graph(cycle_data, result_folder="."):
    cycles = [c for c, _, _, _, _ in cycle_data]
    target_max = [target_hi for _, target_hi, _, _, _ in cycle_data]
    target_min = [target_lo for _, _, target_lo, _, _ in cycle_data]
    input_max = [input_hi for _, _, _, input_hi, _ in cycle_data]
    input_min = [input_lo for _, _, _, _, input_lo in cycle_data]

    target_err_lower = [target_max[i] - target_min[i] for i in range(len(cycles))]
    input_err_lower = [input_max[i] - input_min[i] for i in range(len(cycles))]
    zero_err = [0] * len(cycles)

    fig, ax = plt.subplots()

    ax.errorbar(
        cycles, target_max,
        yerr=[target_err_lower, zero_err],
        fmt='-', capsize=2,
        label='Target Similarity (Max/Min)',
        ecolor='gray'
    )

    ax.errorbar(
        cycles, input_max,
        yerr=[input_err_lower, zero_err],
        fmt='-', capsize=2,
        label='Input Similarity (Max/Min)',
        ecolor='gray'
    )

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

    save_path = os.path.join(result_folder, "similarity_trend.png")
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved: {save_path}")

    plt.close(fig)
    
def batch_score(chunk, current_inputs, target_protein, stop_event=None):
    scored_chunk = []
    for rep, hist in chunk:
        if stop_event and stop_event.is_set():
            break
        target_score, stepwise_score = score_replicate(rep, current_inputs, target_protein)
        scored_chunk.append((rep, hist, target_score, stepwise_score))
    return scored_chunk

def simulate_multiple_cycles(input_sequence, target_sequences, num_cycles, num_replications_per_cycle,
                              mutation_rate, sub_ratio, indel_ratio, tran_ratio, transv_ratio,
                              queue=None, output_folder=".", top_k=1, mutation_rate_str=None, stop_event=None):

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    result_folder = os.path.join(output_folder, timestamp)
    os.makedirs(result_folder, exist_ok=True)

    def log(msg):
        now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        full_msg = f"{now} {msg}"
        if queue:
            queue.put(('log', full_msg))
        else:
            print(full_msg)
        with open(os.path.join(result_folder, "simulation_log.txt"), 'a', encoding='utf-8') as f:
            f.write(full_msg + "\n")
    
    settings_info = f"""
    Simulation started
    ------------------------- Setting Information -------------------------
    ○ Mutation Rate: {mutation_rate_str}
    ○ Substitution Ratio: {sub_ratio}, Indel Ratio: {indel_ratio}
    ○ Transition Ratio: {tran_ratio}, Transversion Ratio: {transv_ratio}
    ○ Number of Cycles: {num_cycles}
    ○ Number of Replications per Cycle: {num_replications_per_cycle}
    ○ Top-N selection: {top_k}
    ○ Input Sequence Length: {len(input_sequence)} nt
    ------------------------------------------------------------------------
    """
    log(settings_info.strip())

    prot_initial = translate(input_sequence)
    target_protein = translate(target_sequences[0][0])

    mutation_args = {
        "mutation_rate": mutation_rate,
        "sub_ratio": sub_ratio,
        "indel_ratio": indel_ratio,
        "tran_ratio": tran_ratio,
        "transv_ratio": transv_ratio
    }

    current_input_sequences = [(input_sequence, [input_sequence])]
    best_similarity = 0
    best_replicate = None
    same_count = 0
    cycle_data = []
    cpu_count = os.cpu_count() or 1
    num_workers = min(61, cpu_count)

    with open(os.path.join(result_folder, "cycle_results.csv"), "w", newline='', encoding="utf-8") as f, ProcessPoolExecutor(max_workers=num_workers) as executor:

        writer = csv.writer(f)
        writer.writerow(["Cycle", "InputSequence", "SelectedSequence",
                         "InputProteinSimilarity", "StepwiseProteinSimilarity",
                         "TargetProteinSimilarity", "InputProteinSequence",
                         "OutputProteinSequence"])

        for cycle in range(num_cycles):
            all_replicates = []
            for seq, history in current_input_sequences:
                replicated = replicate_sequence(seq, history, num_replications_per_cycle, **mutation_args)
                all_replicates.extend(replicated)
    
            futures = {
                executor.submit(score_replicate, rep, [s for s, _ in current_input_sequences], target_protein): (rep, hist)
                for rep, hist in all_replicates
            }
    
            scored = []
    
            for future in as_completed(futures):
                if stop_event and stop_event.is_set():
                    log("🛑 Stop requested during scoring. Aborting current cycle.")
                    for f in futures:
                        f.cancel()
                    break
    
                try:
                    rep, hist = futures[future]
                    target_sim, step_sim = future.result()
                    scored.append((rep, hist, target_sim, step_sim))
                except Exception as e:
                    log(f"⚠️ Error in scoring: {e}")
    
            if not scored:
                log("⚠️ No scored results this cycle.")
                break

            top = sorted(scored, key=lambda x: x[2], reverse=True)[:top_k]
            current_input_sequences = [(rep, history) for rep, history, _, _ in top]

            if (cycle + 1) % 10 == 0:
                best_rep = max(top, key=lambda x: x[2])
                rep_seq, _, best_sim, _ = best_rep
                with open(os.path.join(result_folder, "best_replicates.fasta"), "a") as fasta_file:
                    fasta_file.write(f">Cycle{cycle+1}_best_replicate_sim{best_sim:.2f}\n")
                    fasta_file.write(rep_seq + "\n\n")
                    
            if (cycle + 1) % 100 == 0:
                translate_cached.cache_clear()
                compare_proteins.cache_clear()
                log("Cache cleared (every 100 cycles)")

            similarities = [sim for _, _, sim, _ in top]
            if similarities:
                min_sim = min(similarities)
                max_sim = max(similarities)
                log(f"[Cycle {cycle+1}] Top {top_k} Similarity Range: {min_sim:.2f}% ~ {max_sim:.2f}%")

            for rep, history, target_sim, step_sim in top:
                prot_output = translate(rep)
                translated_input = translate(history[-2]) 

                prot_step = compare_proteins(prot_output, translated_input)
                prot_inout = compare_proteins(prot_output, prot_initial)
                prot_target = compare_proteins(prot_output, target_protein)

                writer.writerow([
                    cycle + 1, history[-2], rep,
                    f"{prot_inout:.2f}%", f"{prot_step:.2f}%", f"{prot_target:.2f}%",
                    translated_input, prot_output
                ])
                
                if target_sim > best_similarity:
                    best_similarity = target_sim
                    best_replicate = rep
                
            target_similarities = [compare_proteins(translate(rep), target_protein) for rep, _ in current_input_sequences]
            input_similarities = [compare_proteins(translate(rep), prot_initial) for rep, _ in current_input_sequences]

            cycle_data.append((
                cycle + 1,
                max(target_similarities), min(target_similarities),
                max(input_similarities), min(input_similarities)
            ))
            
            log(f"[Cycle {cycle+1}] ✅ Best similarity so far: {best_similarity:.2f}%")

            same_reps = sum(1 for rep, history in current_input_sequences if history[-1] == history[-2])
            same_count += same_reps
            if same_reps == 0:
                log(f"[Cycle {cycle+1}] All replicates mutated")
            else:
                log(f"[Cycle {cycle+1}] {(same_reps / top_k) * 100:.1f}% Input protein sequence maintained in this cycle")
            
            all_replicates = None
            scored = None
            futures = None
            gc.collect()
           
            if queue:
                queue.put(('progress', (cycle + 1, num_cycles)))

    if stop_event and stop_event.is_set():
        log("🛑 Simulation was manually stopped.")            
    else:
        log("✅ Simulation completed normally.")

    if cycle_data:
        try:
            plot_similarity_graph(cycle_data, result_folder)
        except Exception as e:
            log(f"⚠️ Failed to generate similarity graph: {e}")    
            
    log(f"Input sequence maintained: {same_count}/{num_cycles * top_k} ({(same_count / (num_cycles * top_k)) * 100:.1f}%)")

    if best_replicate:
        try:
            append_simulation_result_to_csv(
                os.path.join(result_folder, "Final_best_replicate.csv"),
                input_sequence, best_replicate
            )
            log("Final best replicate saved")
        except Exception as e:
            log(f"⚠️ Failed to save final best replicate: {e}")        
    else:
        log("No overall best replicate found.")

    if queue:
        queue.put(('done', None))