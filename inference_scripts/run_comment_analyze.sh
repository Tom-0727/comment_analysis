# bash ./inference_scripts/run_pipeline.sh
python points_extract.py --api_key_yaml_path openai_keys.yaml \
    --model gpt-4.1-2025-04-14 \
    --arch openai \
    --criteria standing_desk \
    --template standing_desk \
    --read_mode amz_xlsx \
    --file_path ./buffer/B0DPKFNBKR-US-Reviews-20250515.xlsx \
    --output_path ./buffer/B0DPKFNBKR-US-Reviews-20250515-Points.csv

python data_analyze.py --file_path ./buffer/B07V6ZSHF4-US-Reviews-Points.csv \
    --output_path ./buffer/tmp_ana.xlsx \
    --criteria_path ./docs/standing_desk_criteria.csv