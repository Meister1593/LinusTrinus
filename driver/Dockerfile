ARG ARCH_TARGET=unset_target
ARG DRIVER_NAME=unset_driver

FROM debian:11 as builder
LABEL stage=linus-trinus-builder
RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get -y install gcc g++ libjsoncpp-dev patch make cmake qtbase5-dev libglew-dev 

FROM builder as build_openvr_preparation
LABEL stage=linus-trinus-builder
COPY . /home/driver
WORKDIR /home/driver
ADD https://github.com/ValveSoftware/openvr/archive/refs/tags/v1.16.8.tar.gz .
RUN tar -xzf v1.16.8.tar.gz
WORKDIR openvr-1.16.8
ADD https://github.com/ValveSoftware/openvr/pull/594.patch openvr-fix-vsprintf_s.patch
ADD https://github.com/ValveSoftware/openvr/pull/1178.patch openvr-use-system-jsoncpp.patch
ADD https://github.com/ValveSoftware/openvr/pull/1524.patch openvr-fix-1.6.18-include.patch
RUN patch -Np1 -i openvr-fix-vsprintf_s.patch
RUN patch -Np1 -i openvr-use-system-jsoncpp.patch
RUN patch -Np1 -i openvr-fix-1.6.18-include.patch
RUN patch -Np1 -i /home/driver/0001-Add-include-stdarg.h-to-strtools_public.cpp.patch

FROM build_openvr_preparation as build_openvr
LABEL stage=linus-trinus-builder
WORKDIR /home/driver
RUN cmake -B build -S openvr-1.16.8 \
	-DCMAKE_INSTALL_PREFIX=/usr \
	-DBUILD_SHARED=1 \
	-DUSE_SYSTEM_JSONCPP=False && \
	make -C build

FROM build_openvr as install_openvr
LABEL stage=linus-trinus-builder
RUN make -C build install

FROM install_openvr as build_driver
LABEL stage=linus-trinus-builder
ARG ARCH_TARGET
ARG DRIVER_NAME
RUN mkdir -p /root/.config/openvr && touch /root/.config/openvr/openvrpaths.vrpath
RUN cmake . -DCMAKE_PREFIX_PATH=/usr/lib/cmake -DCMAKE_BUILD_TYPE=Release && \
	make -j$(expr $(grep -c ^processor /proc/cpuinfo) - 1)
RUN mkdir -p /out/${DRIVER_NAME}/bin/${ARCH_TARGET} && \
	cp -r bin/drivers/${DRIVER_NAME} /out/ && \
	cp -r bin/${ARCH_TARGET}/* /out/${DRIVER_NAME}/bin/${ARCH_TARGET}

