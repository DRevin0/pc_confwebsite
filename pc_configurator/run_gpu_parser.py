import subprocess

def run_gpu_parser(gpu_name):
    subprocess.run([
        "scrapy", "crawl", "technicalcity_spider",
        "-a", f"gpu_name={gpu_name}"
    ])
