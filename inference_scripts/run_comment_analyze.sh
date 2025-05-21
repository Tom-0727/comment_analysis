# bash ./inference_scripts/run_comment_analyze.sh
# arch: openai, qwen, api2d
folder_path="./buffer/卧室扇listing分析评论/"
save_path="./buffer/ceiling_fan_set/"

mkdir -p "$save_path"

for file in "$folder_path"*.xlsx; do
    echo "Processing: $file"

    # 提取原始文件名（不含路径和扩展名）
    filename=$(basename -- "$file")
    filename_noext="${filename%.*}"

    # 设置中间产物和最终输出路径（根据原文件名构造）
    points_path="${save_path}${filename_noext}_points.csv"
    final_output="${save_path}${filename_noext}_analyzed.xlsx"
    echo $points_path


    python points_extract.py --api_key_yaml_path openai_keys.yaml \
        --model gpt-4.1-2025-04-14 \
        --arch openai \
        --criteria ceiling_fan \
        --template ceiling_fan \
        --read_mode amz_xlsx \
        --file_path "$file" \
        --output_path "$points_path"\
        --to_translate False\
        --to_inspect False

    python data_analyze.py --file_path "$points_path" \
        --output_path "$final_output" \
        --criteria_path ./modules/criterias/ceiling_fan_criteria.csv

done


