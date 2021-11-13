#!/bin/bash

if ((1 << 32)); then
  ARCH_TARGET=linux64
else
  ARCH_TARGET=linux32
fi

DRIVER_NAME=linus_trinus
STEAM_FOLDER=~/.steam/steam
STEAMVR_FOLDER=$STEAM_FOLDER/steamapps/common/SteamVR
DOCKER_IMAGE_NAME=linus-trinus-build

# Building
docker build -t ${DOCKER_IMAGE_NAME} --build-arg ARCH_TARGET=${ARCH_TARGET} --build-arg DRIVER_NAME=${DRIVER_NAME} .

# Copying to steamvr folder
docker cp $(docker create --rm linus-trinus-build):/out .
rm -r $STEAMVR_FOLDER/drivers/$DRIVER_NAME
cp -r out/$DRIVER_NAME $STEAMVR_FOLDER/drivers/

# Cleanup
rm -r ./out

get_image_containers() {
	docker ps -a | awk -v i="^$1.*" '{if($2~i){print$1}}'
}

stop_image_containers() {
	docker stop $(get_image_containers $1)
}

read -p 'Delete docker containers created in process? (Y/n): ' docker_delete
docker_delete=${docker_delete:-Y}

if [[ "$docker_delete" == "Y" ]]; then
	docker rm $(stop_image_containers ${DOCKER_IMAGE_NAME} | tr '\n' ' ')
	docker image rm ${DOCKER_IMAGE_NAME}
else
	echo "Not deleting docker image."
fi
