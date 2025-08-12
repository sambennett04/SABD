#positional argument 1 = project_name
#positional argument 2 = project_path
#positional argument 3 = json_parameters_file_name
#path_to_saved_SABD_model already specified in sabd_load_test.py

#reformat json issues into one jsonl file
python3 /scratch/projects/sam/repos/SABD_Replication_SB/data_processing/json_to_jsonl.py --project_name $1 --project_path $2

#create test set
python data/create_testset_json.py --project_name $1 --project_path $2 --dev_perc=0.05

#clean initial jsonl/bug database file for better textual comparison
python data/clean_data_sea_pipeline.py --project_name $1 --project_path $2 --fields short_desc description --type soft --rm_punc --lower_case --rm_number --stop_words --stem --rm_char

#use saved SABD model for inference on our data
CUDA_VISIBLE_DEVICES=0 python experiments/sabd_load_test.py -F ./experiments with ./json_parameters/$3 "recall_rate.window=365"


