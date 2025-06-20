import subprocess
import argparse
import os
import sys
import json
import time


def get_video_info(input_path):
    """Lấy thông tin chi tiết về video"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,pix_fmt,duration,avg_frame_rate,codec_name',
        '-show_entries', 'format=bit_rate',
        '-of', 'json',
        input_path
    ]

    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        info = json.loads(result.stdout)
        stream = info['streams'][0]

        # Tính toán FPS
        fps_fraction = stream['avg_frame_rate'].split('/')
        fps = int(fps_fraction[0]) / int(fps_fraction[1]) if len(fps_fraction) == 2 else float(fps_fraction[0])

        return {
            'width': int(stream['width']),
            'height': int(stream['height']),
            'pix_fmt': stream['pix_fmt'],
            'duration': float(stream.get('duration', 0)),
            'fps': fps,
            'codec': stream['codec_name'],
            'bitrate': info['format'].get('bit_rate', '0')
        }
    except Exception as e:
        print(f"Lỗi khi lấy thông tin video: {str(e)}")
        return None


def advanced_upscale(input_path, output_path, target_width=3840, target_height=2160):
    """
    UPSCALE CHẤT LƯỢNG CAO - PHIÊN BẢN FIX LỖI
    """

    # Lấy thông tin video
    video_info = get_video_info(input_path)
    if not video_info:
        print("Không thể lấy thông tin video. Sử dụng giá trị mặc định...")
        original_width, original_height = 720, 1280
    else:
        original_width, original_height = video_info['width'], video_info['height']
        print(f"Thông tin video gốc:")
        print(f"- Độ phân giải: {original_width}x{original_height}")
        print(f"- Định dạng pixel: {video_info['pix_fmt']}")
        print(f"- Codec: {video_info['codec']}")
        print(f"- Bitrate: {int(video_info['bitrate']) / 1000000:.2f} Mbps" if video_info[
                                                                                   'bitrate'] != '0' else "- Bitrate: Không xác định")
        print(f"- FPS: {video_info['fps']:.2f}")
        print(f"- Thời lượng: {video_info['duration'] / 60:.2f} phút")

    # CHUỖI BỘ LỌC ĐÃ SỬA - ĐƠN GIẢN HÓA VÀ TỐI ƯU
    vf_chain = []

    # 1. Chuyển đổi định dạng pixel chuẩn (quan trọng cho yuvj420p)
    vf_chain.append("format=yuv420p")

    # 2. Khử nhiễu nhẹ - sử dụng giá trị mặc định an toàn
    vf_chain.append("hqdn3d")

    # 3. Upscale với thuật toán bicubic (ổn định nhất)
    vf_chain.append(f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease:flags=bicubic")

    # 4. Thêm viền đen
    vf_chain.append(f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:color=black")

    # 5. Làm nét nhẹ - sử dụng unsharp với tham số an toàn
    vf_chain.append("unsharp=5:5:0.8:5:5:0.6")

    vf_string = ",".join(vf_chain)

    # Xây dựng lệnh FFmpeg đơn giản
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-vf', vf_string,
        '-c:v', 'libx264',
        '-crf', '18',  # Chất lượng tốt
        '-preset', 'medium',  # Cân bằng giữa tốc độ và chất lượng
        '-profile:v', 'high',
        '-level', '5.1',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-movflags', '+faststart',
        '-y',  # Ghi đè
        output_path
    ]

    try:
        print(f"\nBắt đầu upscale lên {target_width}x{target_height}...")
        print(f"Chuỗi bộ lọc đơn giản: {vf_string}")
        print(f"Lệnh FFmpeg: {' '.join(cmd)}")

        # Chạy FFmpeg với hiển thị trực tiếp
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        # Hiển thị output trực tiếp
        for line in process.stdout:
            print(line, end='')
            sys.stdout.flush()

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)

        print("\nUpscale hoàn tất thành công!")
        print(f"Video đầu ra: {os.path.abspath(output_path)}")

    except subprocess.CalledProcessError as e:
        print(f"\nLỗi trong quá trình xử lý (mã lỗi {e.returncode})")
        print("Nguyên nhân có thể do:")
        print("1. FFmpeg không hỗ trợ bộ lọc")
        print("2. Video đầu vào có vấn đề")
        print("3. Thiếu bộ nhớ hoặc tài nguyên hệ thống")

        # Kiểm tra phiên bản FFmpeg
        try:
            subprocess.run(['ffmpeg', '-version'], check=True)
        except:
            print("\nCẢNH BÁO: Không tìm thấy FFmpeg hoặc phiên bản quá cũ!")
            print("Vui lòng cài đặt FFmpeg phiên bản mới nhất từ https://ffmpeg.org/download.html")

        sys.exit(1)
    except FileNotFoundError:
        print("\nFFmpeg không được tìm thấy. Vui lòng cài đặt FFmpeg và thêm vào PATH.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nĐã dừng bởi người dùng")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upscale video - Phiên bản sửa lỗi')
    parser.add_argument('input', help='Đường dẫn video gốc')
    parser.add_argument('output', help='Đường dẫn video đầu ra')
    parser.add_argument('--width', type=int, default=3840,
                        help='Chiều rộng đích (mặc định: 3840)')
    parser.add_argument('--height', type=int, default=2160,
                        help='Chiều cao đích (mặc định: 2160)')

    args = parser.parse_args()

    # Kiểm tra file đầu vào
    if not os.path.isfile(args.input):
        print(f"Lỗi: Không tìm thấy file đầu vào - {args.input}")
        sys.exit(1)

    # Xử lý video với cài đặt đơn giản
    advanced_upscale(
        input_path=args.input,
        output_path=args.output,
        target_width=args.width,
        target_height=args.height
    )