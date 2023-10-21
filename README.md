# iEEG scripts for "Temporal organized..."
# Dependencies 
MNE-python
scikit-learn
nilearn
numpy, pandas, matplotlib

# Task code
Code to run the risk task are all in ./TaskCode  
(requires Matlab and PTB3)

# Behavioural analysis
parseBehav.py # convert .mat to .csv  
behaviour.py  
riskModel.py  

# Neural processing
preprocess.py    

## Functions 
neuralynx_io.py # ported from https://github.com/alafuzof/NeuralynxIO  
channel_functions.py  
epoch_functions.py  
input_function.py  
preprocess_functions.py  
utilities.py  

## Functions_stats
design_functions.py  
decode_functions.py  
generalize_functions.py  
regression_functions.py # adapted from https://gist.github.com/brentp/5355925  

## Figures 
plot_model_revised.py 
plot_num_contacts.py 
plot_nodes_coords.py  
plot_nodes_decoding.py # Feature importance topoplot  

