# -*- coding: utf-8 -*-
# Module: Webtoon-RIPPER
# Created on: 03-01-2024
# Authors: -∞WKS∞-/Varyg1001
# Version: 1.0.0

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
parser.add_argument("-o", dest="output_format", default="pdf", choices=["pdf", "cbz"], help="Output format (pdf or cbz)")
args = parser.parse_args()

url_base = args.webtoon_url
collected_info = []
page_number = 1

while True:
    response = requests.get(f"{url_base}&page={page_number}")
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

jpg_folder = 'downloaded_images/jpg'
png_folder = 'downloaded_images/png'
pdf_folder = 'downloaded_pdfs'
os.makedirs(jpg_folder, exist_ok=True)
os.makedirs(png_folder, exist_ok=True)
os.makedirs(pdf_folder, exist_ok=True)

console.print("\nDownloading images and converting to PDF/CBZ:")

for url, text in collected_info:
    if args.output_format == "pdf":
        output_path = os.path.join(pdf_folder, f"{text}.pdf")
    elif args.output_format == "cbz":
        output_path = os.path.join(pdf_folder, f"{text}.cbz")
    else:
        console.print("Invalid output format specified.")
        break

    if os.path.exists(output_path):
        console.print(f"[cyan]{output_path}[/cyan] already exists. Skipping image download.")
        continue

    console.print(f"Downloading [cyan]{text}[/cyan]")
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
    png_images = []
    image_paths = []

    with Progress() as progress:
        task = progress.add_task("[cyan]Downloading and converting images[/cyan]", total=len(image_tags), columns=[TimeRemainingColumn(elapsed_when_finished=True, compact=True)])
        
        for idx, image_tag in enumerate(image_tags, start=1):
            progress.advance(task)
            data_url = image_tag.get('data-url')
            img_response = requests.get(data_url, headers=headers)

            img_path = os.path.join(jpg_folder, f'image_{idx}.png')
            with open(img_path, 'wb') as img_file:
                img_file.write(img_response.content)
            
            image_paths.append(img_path)

            if img_path.lower().endswith('.png'):
                png_images.append(Image.open(img_path).convert('RGB'))
            else:
                jpg_images.append(Image.open(img_path).convert('RGB'))

    if jpg_images or png_images:
        if args.output_format == "pdf":
            pdf_images = jpg_images + png_images
            pdf_images[0].save(output_path, save_all=True, append_images=pdf_images[1:])
        elif args.output_format == "cbz":
            with ZipFile(output_path, 'w') as cbz_file:
                for idx, img_path in enumerate(image_paths, start=1):
                    cbz_file.write(img_path, f'image_{idx}.png')

        for idx in range(1, len(image_tags) + 1):
            img_path = os.path.join(jpg_folder, f'image_{idx}.png')
            if os.path.exists(img_path):
                os.remove(img_path)

        console.print(f"Images downloaded, converted to {args.output_format.upper()}, and saved as '[cyan]{output_path}[/cyan]'.")
    else:
        console.print(f"No images found for [cyan]{text}[/cyan].")
