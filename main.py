# -*- coding: utf-8 -*-
# Module: Webtoon-RIPPER
# Created on: 03-01-2024
# Authors: -∞WKS∞-/Varyg1001
# Version: 1.0.1

import os
from PIL import Image
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress, TimeRemainingColumn
from rich import print
import argparse
from zipfile import ZipFile

console = Console()

parser = argparse.ArgumentParser(description="Webtoon-RIPPER")
parser.add_argument("-url", dest="webtoon_url", required=True, help="URL of the webtoon")
parser.add_argument("-o", dest="output_format", default="both", choices=["pdf", "cbz", "both"], help="Output format (pdf, cbz, both)")
args = parser.parse_args()

# Web scraping to get the webtoon title
response = requests.get(args.webtoon_url)
soup = BeautifulSoup(response.text, 'html.parser')
og_title_meta = soup.find('meta', {'property': 'og:title'})
og_title_content = og_title_meta.get('content') if og_title_meta else None
webtoon_title = og_title_content.strip() if og_title_content else "Untitled"

# Folder structure
download_folder = 'download'
webtoon_folder = os.path.join(download_folder, webtoon_title)
jpg_folder = os.path.join(webtoon_folder, 'jpg')
pdf_folder = os.path.join(webtoon_folder, 'pdf')
cbz_folder = os.path.join(webtoon_folder, 'cbz')
os.makedirs(jpg_folder, exist_ok=True)
os.makedirs(pdf_folder, exist_ok=True)
os.makedirs(cbz_folder, exist_ok=True)

collected_info = []
page_number = 1

while True:
    response = requests.get(f"{args.webtoon_url}&page={page_number}")
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        ul_tag = soup.find('ul', {'id': '_listUl'})
        subj_spans = ul_tag.select('span.subj span')
        a_tags = ul_tag.find_all('a')
        new_info_found = False

        if subj_spans or a_tags:
            for subj_span, a_tag in zip(subj_spans, a_tags):
                href_attribute = a_tag.get('href')
                text_content = subj_span.text
                if (href_attribute, text_content) not in collected_info:
                    collected_info.append((href_attribute, text_content))
                    new_info_found = True

            if not new_info_found:
                console.print("All information has been found.")
                break

            page_number += 1
            console.print(f"Searching for information on page {page_number}")
        else:
            console.print("All information has been found.")
            break
    else:
        console.print(f"Error: [bold red]{response.status_code}[/bold red]")
        break

collected_info.reverse()

# Download and conversion
console.print("\nDownloading images and converting to PDF/CBZ:")

for url, text in collected_info:
    # Dynamically creating output paths based on the webtoon title
    pdf_output_path = os.path.join(pdf_folder, f"{text}.pdf")
    cbz_output_path = os.path.join(cbz_folder, f"{text}.cbz")

    if args.output_format == "pdf" or args.output_format == "both":
        if os.path.exists(pdf_output_path):
            console.print(f"[cyan]{pdf_output_path}[/cyan] already exists. Skipping image download.")
        else:
            console.print(f"Downloading [cyan]{text}[/cyan] for PDF")
            headers = {
                'authority': 'www.webtoons.com',
                'referer': 'https://www.webtoons.com/',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0',
            }
            response = requests.get(url, headers=headers)
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            image_tags = soup.find_all('img', class_='_images')

            jpg_images = []
            pdf_images = []
            image_paths = []

            with Progress() as progress:
                task = progress.add_task("[cyan]Downloading and converting images for PDF[/cyan]", total=len(image_tags), columns=[TimeRemainingColumn(elapsed_when_finished=True, compact=True)])

                for idx, image_tag in enumerate(image_tags, start=1):
                    progress.advance(task)
                    data_url = image_tag.get('data-url')
                    img_response = requests.get(data_url, headers=headers)

                    img_path = os.path.join(jpg_folder, f'image_{idx}.png')
                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_response.content)

                    image_paths.append(img_path)

                    jpg_images.append(Image.open(img_path).convert('RGB'))

            if jpg_images:
                pdf_images = jpg_images
                pdf_images[0].save(pdf_output_path, save_all=True, append_images=pdf_images[1:])
                console.print(f"Images downloaded, converted to PDF, and saved as '[cyan]{pdf_output_path}[/cyan]'.")
            else:
                console.print(f"No images found for [cyan]{text}[/cyan] in PDF mode.")

    if args.output_format == "cbz" or args.output_format == "both":
        if os.path.exists(cbz_output_path):
            console.print(f"[cyan]{cbz_output_path}[/cyan] already exists. Skipping image download.")
        else:
            console.print(f"Downloading [cyan]{text}[/cyan] for CBZ")
            headers = {
                'authority': 'www.webtoons.com',
                'referer': 'https://www.webtoons.com/',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0',
            }
            response = requests.get(url, headers=headers)
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            image_tags = soup.find_all('img', class_='_images')

            image_paths = []

            with Progress() as progress:
                task = progress.add_task("[cyan]Downloading images for CBZ[/cyan]", total=len(image_tags), columns=[TimeRemainingColumn(elapsed_when_finished=True, compact=True)])

                for idx, image_tag in enumerate(image_tags, start=1):
                    progress.advance(task)
                    data_url = image_tag.get('data-url')
                    img_response = requests.get(data_url, headers=headers)

                    img_path = os.path.join(jpg_folder, f'image_{idx}.png')
                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_response.content)

                    image_paths.append(img_path)

            if image_paths:
                with ZipFile(cbz_output_path, 'w') as cbz_file:
                    for idx, img_path in enumerate(image_paths, start=1):
                        cbz_file.write(img_path, f'image_{idx}.png')
                console.print(f"Images downloaded, converted to CBZ, and saved as '[cyan]{cbz_output_path}[/cyan]'.")
            else:
                console.print(f"No images found for [cyan]{text}[/cyan] in CBZ mode.")
