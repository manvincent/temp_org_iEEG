# iEEG / ECoG Scripts  
Scripts are ordered by sequence  
Scripts with the same number can be done in either order, but letter indicates preferred sequence   

## 1.Formating and preprocessing  
1.1) convert_ncs2mne.py  
1.2) preprocess.py  
1.3) specifyChannels.py
1.4) ROI_chan_parse.py 

## 2.Data wrangling  
Scripts for parsing / epoching data  
### 2.1.LFP  
2.1) epoch_parse_LFP.py  

# Statistical modelling  
3.1) glm_setup_design.py  
3.x) pval_fdr.py # Outputs statistics tables for neural results

# Behavioural analysis
4.1) inferBehav_ephys.py
## Plotting code
Scripts for plotting 
### Channel localisation
plot_nodes.py
plot_nodes_decoding.py # Feature importance topoplot
plot_model_revised.py

### Statistical results
plot_decode_CI.py # Also outputs supplementary table

