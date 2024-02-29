from uvctypes import *
import cv2
from queue import Queue
import numpy as np

BUF_SIZE = 2
q = Queue(BUF_SIZE)

def py_frame_callback(frame, userptr):

    array_pointer = cast(frame.contents.data, POINTER(c_uint16 * (frame.contents.width * frame.contents.height)))
    data = np.frombuffer(
        array_pointer.contents, dtype=np.dtype(np.uint16)
    ).reshape(
        frame.contents.height, frame.contents.width
    )

    if frame.contents.data_bytes != (2 * frame.contents.width * frame.contents.height):
        return

    if not q.full():
        q.put(data)

PTR_PY_FRAME_CALLBACK = CFUNCTYPE(None, POINTER(uvc_frame), c_void_p)(py_frame_callback)

def main():
    
    ctx = POINTER(uvc_context)()
    dev = POINTER(uvc_device)()
    devh = POINTER(uvc_device_handle)()
    ctrl = uvc_stream_ctrl()
    
    res  = libuvc.uvc_init(byref(ctx), 0)
    
    # uvc-device 체크
    if res < 0:
        print(f'uvc_init error')
        exit(1)
    try:
        res = libuvc.uvc_find_device(ctx, )
    except:
        print('uvc_find_device error')
        exit(1)
    try:
        res = libuvc.uvc_open(dev, byref(devh))
    except:
        print('uvc_open error')
        exit(1)
    
    # uvc-device 연결 완료
    print('device opened!')
    print_device_info(devh)
    print_device_formats(devh)
    
    # uvc-device data 포메팅 확인
    frame_formats = uvc_get_frame_formats_by_guid(devh, VS_FMT_GUID_Y16)
    if len(frame_formats) == 0:
        print('device does not support Y16')
        exit(1)
    
    # 데이터 받아서 열어두기(스트리밍 상태임)
    res = libuvc.uvc_start_streaming(devh, byref(ctrl), PTR_PY_FRAME_CALLBACK, None, 0)
    if res < 0:
        print(f'uvc_start_striming failed : {res}')
    
    while True:
        data = q.get(True,500)
        if data is None:
            break
        print(type(data))