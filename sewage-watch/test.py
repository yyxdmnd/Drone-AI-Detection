import cv2
import os
from tqdm import tqdm
import argparse

def images_to_video(image_folder, output_video, display_time=2.0, image_size=None):
    """
    将文件夹中的图像序列转换为MP4视频，每张图片停留指定时间
    
    参数:
        image_folder: 包含图像的文件夹路径
        output_video: 输出视频文件路径(.mp4)
        display_time: 每张图片显示时间(秒)，默认2秒
        image_size: 输出视频的尺寸(宽,高)，None则使用第一帧的尺寸
    """
    # 获取文件夹中所有图像文件
    images = [img for img in os.listdir(image_folder) 
              if img.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif'))]
    images.sort()  # 按文件名排序
    
    if not images:
        print(f"错误: 文件夹 {image_folder} 中没有找到图像文件")
        return
    
    print(f"找到 {len(images)} 张图像，正在转换为视频(每张停留{display_time}秒)...")
    
    # 读取第一张图像获取尺寸
    first_image = cv2.imread(os.path.join(image_folder, images[0]))
    if first_image is None:
        print(f"错误: 无法读取第一张图像 {images[0]}")
        return
    
    height, width, _ = first_image.shape
    if image_size is not None:
        width, height = image_size
    
    # 固定帧率为25fps，然后计算每张图片需要的帧数
    fps = 25
    frames_per_image = int(fps * display_time)
    
    # 定义视频编码器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4编码器
    video_writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    if not video_writer.isOpened():
        print("错误: 无法创建视频文件")
        return
    
    # 处理每张图像
    for image_name in tqdm(images):
        image_path = os.path.join(image_folder, image_name)
        frame = cv2.imread(image_path)
        
        if frame is None:
            print(f"警告: 无法读取图像 {image_name}，跳过")
            continue
        
        # 调整图像尺寸
        if (frame.shape[1], frame.shape[0]) != (width, height):
            frame = cv2.resize(frame, (width, height))
        
        # 写入多次以实现停留时间
        for _ in range(frames_per_image):
            video_writer.write(frame)
    
    # 释放资源
    video_writer.release()
    print(f"视频已成功保存到 {output_video}")
    print(f"视频总时长: {len(images)*display_time:.1f}秒")

if __name__ == "__main__":
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='将图像文件夹转换为MP4视频(每张图片停留指定时间)')
    parser.add_argument('--input', type=str, required=True, help='输入图像文件夹路径')
    parser.add_argument('--output', type=str, default='output.mp4', help='输出视频文件路径')
    parser.add_argument('--time', type=float, default=2.0, help='每张图片显示时间(秒)，默认2秒')
    parser.add_argument('--width', type=int, help='输出视频宽度')
    parser.add_argument('--height', type=int, help='输出视频高度')
    
    args = parser.parse_args()
    
    # 确定输出尺寸
    size = None
    if args.width and args.height:
        size = (args.width, args.height)
    
    # 调用转换函数
    images_to_video(
        image_folder=args.input,
        output_video=args.output,
        display_time=args.time,
        image_size=size
    )