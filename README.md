# Random mutation and similarity-based selection(RMSS)
A graphical Python tool for simulating virus replication that incorporates random mutation and similarity-based selection, with support for customization of parameters such as substitution rate, substitution/indel ratio, and transition/transversion ratio.

## Project Overview
This tool simulates the evolutionary process of a coding sequence (CDS) by introducing random mutations and applying similarity-based selection over multiple cycles.

Users provide an input and a target sequence in FASTA format, and configure mutation parameters such as substitution rate, substitution/indel ratio, and transition/transversion ratio. For each cycle, the user also configures how many replicates to generate, and how many top-N sequences to select as input for the next cycle.

Through successive cycles of mutation and selection, this tool helps explore potential intermediate sequences between the input and the target.

## Windows Executable
- `RMSS_viral_protein_simulator_ver2.2.exe`: General user version  

## Usage Example
1. Load input `.fasta` file and target `.fasta` file
2. Customize ‘user setting’
3. Choose output folder
4. Run simulation

## File Structure

| File | Description |
|------|-------------|
| `main.py` | Main launcher |
| `simulation_core.py` | Processing logic |
| `simulation_GUI.py` | Processing PySide6-based GUI |
| `Mutation_simulator_GUI.py`| PySide6-based UI |
| `*_ver*.exe` | Windows packaged executables |

## Requirements when you used python cord

```
biopython
matplotlib
```

---

## Third-party Libraries & Licenses

This project uses the following open-source Python libraries:

### Biopython
- **License:** Biopython License (OSI-approved, MIT-like)
- **URL:** https://biopython.org
- **Citation:**  
  Cock PJ et al. (2009). *Biopython: freely available Python tools for computational molecular biology and bioinformatics*. Bioinformatics, 25(11):1422–1423.  
  [DOI: 10.1093/bioinformatics/btp163](https://doi.org/10.1093/bioinformatics/btp163)

### matplotlib
- **License:** PSF License (BSD-like)
- **URL:** https://matplotlib.org
- **Citation:**  
  Hunter, J. D. (2007). *Matplotlib: A 2D graphics environment*. Computing in Science & Engineering, 9(3), 90–95.

### Python Standard Library
- `csv`, `random`, `datetime`, `os`, `sys`, `gc`, `functools`, `tkinter`, `concurrent.futures`
- Included with Python, no separate license needed.
