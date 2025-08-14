Constraint-based In-Station Train Dispatching
=============================================

This repository is the support material for the paper *"Constraint-based In-Station Train Dispatching"*
published and presented at [CP 2025](https://cp2025.a4cp.org/). The [paper](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2025.33) is available in the open-access
proceedings at [Schloss Dagstuhl - Leibniz Zentrum für Informatik](https://drops.dagstuhl.de/entities/volume/LIPIcs-volume-340) or in this repository as [LIPIcs.CP.2025.33.pdf](LIPIcs.CP.2025.33.pdf).

Project contributors:
- Andreas Schutt (Data61, CSIRO, Australia),
- Matteo Cardellini (DIBRIS, University of Genova, Italy),
- Jip J. Dekker (Department of Data Science & AI, Monash University, Australia, and OPTIMA, Melbourne, Australia),
- Daniel Harabor (Department of Data Science & AI, Monash University, Australia),
- Marco Maratea (Department of Mathematics and Informatics, University of Calabria, Italy), and
- Mauro Vallati (Department of Computer Science, University of Huddersfield, UK)

## Repository Organisation

The repository is organized into the following directories:

- `data`:The datasets used in the paper, see [README.md](data/README.md) for more details.
- `model`: All (partial) MiniZinc model files, see [README.md](model/README.md) for more details.
- `raw_results`: Results of individual runs of each solve call made by the experiment scripts (not tracked by git).
- `results`: Aggregated results of the experiments.
- `scripts`: Scripts for running experiments and generating results, see [README.md](scripts/README.md) for more details.

## Reference

If you find the materials in this repository useful and/or you use the data, please cite our paper:
```
@InProceedings{schutt_et_al:LIPIcs.CP.2025.33,
  author =	{Schutt, Andreas and Cardellini, Matteo and Dekker, Jip J. and Harabor, Daniel and Maratea, Marco and Vallati, Mauro},
  title =	{{Constraint-Based In-Station Train Dispatching}},
  booktitle =	{31st International Conference on Principles and Practice of Constraint Programming (CP 2025)},
  pages =	{33:1--33:24},
  series =	{Leibniz International Proceedings in Informatics (LIPIcs)},
  ISBN =	{978-3-95977-380-5},
  ISSN =	{1868-8969},
  year =	{2025},
  volume =	{340},
  editor =	{de la Banda, Maria Garcia},
  publisher =	{Schloss Dagstuhl -- Leibniz-Zentrum f{\"u}r Informatik},
  address =	{Dagstuhl, Germany},
  URL =		{https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2025.33},
  URN =		{urn:nbn:de:0030-drops-238941},
  doi =		{10.4230/LIPIcs.CP.2025.33},
  annote =	{Keywords: in-station train dispatching, train scheduling, railway scheduling, constraint programming, mixed-integer programming}
}
```
