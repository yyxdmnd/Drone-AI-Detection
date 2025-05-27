import axios from 'axios';
import config from '@/config';

const detectionApi = {
  // 上传图片进行检测
  async detectImage(imageFile) {
    try {
      const formData = new FormData();
      formData.append('image', imageFile);
      
      const response = await axios.post(
        `${config.apiBaseUrl}/detection/image/`, 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      console.log('API返回的原始检测结果:', response.data);
      
      // 规范化数据格式
      const result = {
        ...response.data,
      };
      
      // 确保 detections 字段存在且为数组
      if (!result.detections) {
        // 检查是否在其他位置有检测结果
        if (result.result && result.result.detections) {
          result.detections = result.result.detections;
        } else {
          result.detections = [];
          console.log('检测结果中缺少 detections 字段，初始化为空数组');
        }
      }
      
      // 更新为基于 polluted 置信度的判断逻辑
      const pollutedDetection = result.detections.find(detection => 
        detection.class_name.toLowerCase() === 'polluted'
      );
      
      // 如果找到 polluted 且置信度大于 50%，则为污水
      const hasWastewater = pollutedDetection && pollutedDetection.confidence > 0.5;
      
      // 添加污水判断结果
      result.isWastewater = hasWastewater;
      
      console.log('是否检测到污水:', hasWastewater);
      if (pollutedDetection) {
        console.log('污水检测置信度:', pollutedDetection.confidence);
      } else {
        console.log('未检测到 polluted 分类');
      }
      
      // 如果有结果图片URL但没有Base64数据，添加标记以便前端正确处理
      if (result.result_image_url && !result.result_image) {
        result.result_image = result.result_image_url;
      }
      
      // 如果API直接返回了result_image，假设是URL路径
      if (result.result_image && !result.result_image.startsWith('data:image')) {
        // 转换为完整URL
        if (result.result_image.startsWith('/')) {
          result.result_image_url = result.result_image;
        }
      }
      
      console.log('处理后的检测结果:', result);
      return result;
    } catch (error) {
      console.error('图像检测失败:', error);
      throw new Error(`图像检测失败: ${error.response?.data?.error || error.message}`);
    }
  },
  
  // 上传视频进行检测
  async detectVideo(videoFile) {
    try {
      const formData = new FormData();
      formData.append('video', videoFile);
      
      // 视频处理可能需要较长时间，设置较长的超时时间
      const response = await axios.post(
        `${config.apiBaseUrl}/detection/video/`, 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          timeout: 600000 // 10分钟超时
        }
      );
      
      console.log('视频检测API返回结果:', response.data);
      
      // 规范化数据格式
      const result = {
        ...response.data
      };
      
      // 确保 detections_count 字段存在
      if (!result.detections_count && result.detections_count !== 0) {
        result.detections_count = 0;
      }
      
      // 处理视频URL，确保路径完整
      if (result.result_video_url && result.result_video_url.startsWith('/')) {
        // 添加完整的基础URL
        console.log('处理视频URL路径:', result.result_video_url);
      }
      
      console.log('处理后的视频检测结果:', result);
      return result;
    } catch (error) {
      console.error('视频检测失败:', error);
      throw new Error(`视频检测失败: ${error.response?.data?.error || error.message}`);
    }
  }
};

export default detectionApi;
