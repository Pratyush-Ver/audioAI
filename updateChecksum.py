import hashlib
import csv

def get_md5_checksum(file_path):
    with open(file_path, "rb") as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(1024)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

if __name__ == "__main__":
    file_path = "your_file_path"
    md5_checksum = get_md5_checksum(file_path)
    with open("md5_checksum.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file_name", "md5_checksum"])
        writer.writerow([file_path, md5_checksum])