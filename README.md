![license MIT](https://img.shields.io/github/license/kamal0013/PowNet) [![DOI](https://zenodo.org/badge/249703321.svg)](https://zenodo.org/badge/latestdoi/249703321)
# PowNet-Laos: Unit Commitment / Economic Dispatch model for the Laotian power system (with sample data)
This repository contains PowNet-Laos, an implementation of [PowNet](https://github.com/kamal0013/PowNet) model on the Laotian power system. The model is developed based on the power system facilities (power plants, substations, import/export nodes, and high-voltage transmission lines) operated in Laos during the year 2016. The majority of data are extracted from technical reports, publicly available, published by Electricite Du Laos (EDL) and the Department of Energy Policy and Planning (DEPP), Ministry of Energy and Mine, Lao PDR. The input data concerning the production of the hydropower reservoirs are generated via simulation with [VIC-Res](https://github.com/thanhiwer/VICRes). We note that these data could be generated with other hydrological-hydraulic models. Please refer to Chowdhury et al. (2020a) for additional details on (1) the Laotian power system, and (2) PowNet-Laos setup.

The basic functionalities and PowNet input-output structure are described in [Chowdhury et al. (2020b)](https://openresearchsoftware.metajnl.com/articles/10.5334/jors.302/). Step-by-step instructions on how to run and customize PowNet for any power system are provided in this [GitHub repository](https://github.com/kamal0013/PowNet).

# Laotian Power System
The Main generation and transmission components of the Laotian power system are shown in the Figure below (adapted from Chowdhury et al. (2020a)). Note that the hydropower dams are located in the Lower Mekong River basin, as illustrated in the inset.

![](https://github.com/kamal0013/PowNet-Laos/blob/master/Model%20and%20data/fig1_Laotian_grid_mekong.jpg)

# License
PowNet-Laos and the data are released under the MIT license. Please read it carefully before employing the model.

# Citation
If you use PowNet-Laos and/or the data for your research, please cite the following papers:

Chowdhury, A.K., Dang, T.D., Bagchi, A., and Galelli, S., (2020a). Expected benefits of Laos' hydropower development curbed by hydro-climatic variability and limited transmission capacity—opportunities to reform. Journal of Water Resources Planning and Management (in review).

Chowdhury, A.K., Kern, J., Dang, T.D. and Galelli, S., (2020b). PowNet: A Network-Constrained Unit Commitment/Economic Dispatch Model for Large-Scale Power Systems Analysis. Journal of Open Research Software, 8(1), p.5. DOI: http://doi.org/10.5334/jors.302

In addition, each release of PowNet-Laos is achieved on Zenodo with a DOI, that can be found here [![DOI](https://zenodo.org/badge/249703321.svg)](https://zenodo.org/badge/latestdoi/249703321).

# Contact
For questions and feedback related to PowNet-Laos, please send an email to afm.chowdhury@uon.edu.au (AFM Kamal Chowdhury) or stefano_galelli@sutd.edu.sg (Stefano Galelli).

# Acknowledgment	
PowNet-Laos development is supported by Singapore's Ministry of Education (MoE) through the Tier 2 project “Linking water availability to hydropower supply – an engineering systems approach” (Award No. MOE2017-T2-1-143).
