# Webtoon Ripper

Webtoon Ripper is a Python script designed to effortlessly download and organize webtoon images, enabling users to convert them into PDF or CBZ formats seamlessly.

## Features

- **Download**: Fetch webtoon images from a specified URL.
- **Organization**: Organize images into folders for different formats (JPG and PNG).
- **Conversion**: Convert images into either PDF or CBZ format.
- **Progress Visualization**: Track download and conversion progress using the rich library.

## Prerequisites

- Python 3.7
- Install dependencies using the following command:
  ```bash
  pip install -r requirements.txt
  ```

## Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SASUKE-DUCK/webtoon-RIPPER.git
   ```

2. **Navigate to the project directory:**
   ```bash
   cd webtoon-RIPPER
   ```

3. **Run the script with the desired webtoon URL and output format:**
   ```bash
   python main.py -url [WEBTOON_URL] -o [pdf|cbz]
   ```
   Example:
   ```bash
   python main.py -url "https://www.webtoons.com/en/drama/whale-star-the-gyeongseong-mermaid/list?title_no=3237" -o cbz
   ```
   
![image](https://i.imgur.com/bql9y94.png)

## Options

- `-url` : URL of the webtoon series.
- `-o`   : Output format (pdf or cbz).

## Acknowledgments

- [Requests](https://docs.python-requests.org/en/latest/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- [Pillow (PIL Fork)](https://python-pillow.org/)
- [Rich](https://github.com/willmcgugan/rich)

## Contribution

Contributions are welcome! Feel free to open an issue or submit a pull request.

## Author

- [SASUKE-DUCK](https://github.com/SASUKE-DUCK)
```
