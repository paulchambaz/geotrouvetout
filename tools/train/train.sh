#!/bin/bash

get_image() {
  mkdir -p "${name}/images"
  # download the image from open image dataset
  python downloader.py "${name}/image_ids.txt" --download_folder="${name}/images" --num_processes=5
  cat "$annotations_file"| cut -d ',' -f 1 | sed 's/^/train\//' > "${name}/image_ids.txt"
}

get_labels() {
  mkdir -p "${name}/labels"

  # create the bbox files
  labels=$(cat "${annotations_file}" | awk -F ',' '{printf "%s.txt 0 %s %s %s %s\n", $1, $5, $7, $6 - $5, $8 - $7}')

  while read line; do
      filename=$(echo "${line}" | cut -d ' ' -f 1)
      content=$(echo "${line}" | cut -d ' ' -f 2-)
      echo "${content}" >> "${name}/labels/${filename}"
  done <<< "$labels"
}

get_yaml() {
  # create the yaml configuration file
  cat > "${name}/${name}.yaml" << EOF
path: $(pwd)/$name
train: images
val: images

names:
  0: ${name}
EOF
}

[ ! -e downloader.py ] && wget "https://raw.githubusercontent.com/openimages/dataset/master/downloader.py"
[ ! -e train-annotations-bbox.csv ] && wget "https://storage.googleapis.com/openimages/2018_04/train/train-annotations-bbox.csv"
[ ! -e class-descriptions-boxable.csv ] && "wget https://storage.googleapis.com/openimages/2018_04/class-descriptions-boxable.csv"
[ ! -e yolov8.yaml ] && wget "https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/models/v8/yolov8.yaml"
[ ! -e yolov8s.pt ] && wget "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt"

[ -z "$1" ] && echo "Enter a class" && exit 0

chosen=$(grep "$1$" class-descriptions-boxable.csv)
# chosen=$(cat class-descriptions-boxable.csv | fzf --delimiter=',' --with-nth=2)

[ -z "$chosen" ] && echo "Class not present" && exit 0

id=$(echo "${chosen}" | cut -d ',' -f 1)
name=$(echo "${chosen}" | cut -d ',' -f 2)
name=$(echo "${name,,}" | tr ' ' '_')

mkdir -p "${name}"

annotations_file="${name}/train-annotations-bbox.csv"

grep "$id" train-annotations-bbox.csv | head -n 10000 > "$annotations_file"

[ ! -e "${name}/images" ] && get_images

[ ! -e "${name}/labels" ] && get_labels

get_yaml

# train the model
yolo detect train data="${name}/${name}.yaml" model=yolov8s.yaml pretrained=yolov8s.pt epochs=32 imgsz=640 --project=./ --name="${name}_yolo"

# move the new weights to ${name}.pt
mv "${name}_yolo/weights/best.pt" "${name}.pt"
