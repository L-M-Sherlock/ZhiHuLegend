import json
from pathlib import Path
from datetime import datetime, timezone

BASE_URL = "https://l-m-sherlock.github.io/ZhiHuLegend"

nicknames = {
    "ma-qian-zu": "马前卒",
    "huo-hua-de-41": "霍华德",
    "dang.xinran": "立党",
    "li-yin-61-82": "李归农",
    "maple-syrup-41": "tim未来之光",
    "dantes-15": "勃勃",
    "miloyip": "Milo Yip",
    "Himself65": "扩散性百万甜面包",
    "sinya": "李新野",
}


def generate_summary(username: str):
    # Collect all articles
    articles = []
    for file in Path(f"{username}/article").glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["file_stem"] = file.stem
            articles.append(data)

    # Collect all answers
    answers = []
    for file in Path(f"{username}/answer").glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                data["file_stem"] = file.stem
                if "error" in data:
                    print(data["error"], file.stem)
                    file.unlink()
                    continue
                answers.append(data)
            except json.JSONDecodeError:
                print(file.stem, "is not a valid json file")

    # Sort by voteup_count
    articles.sort(key=lambda x: x["voteup_count"], reverse=True)
    answers.sort(key=lambda x: x["voteup_count"], reverse=True)

    # Generate HTML content with tabs
    html_content = (
        f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>知乎索引</title>
        <meta property="og:type" content="website">
        <meta property="og:title" content="知乎索引">
        <meta property="og:site_name" content="ZhiHu Legend">
        <meta property="og:url" content="https://l-m-sherlock.github.io/ZhiHuLegend/">
        <meta name="description" property="og:description" content="{nicknames[username]}的知乎文章和回答索引">
        <meta name="google-site-verification" content="U7ZAFUgGNK60mmMqaRygg5vy-k8pwbPbDFXNjDCu7Xk" />
        <meta property="twitter:card" content="summary">
        <meta name="twitter:title" property="og:title" itemprop="name" content="知乎索引">
        <meta name="twitter:description" property="og:description" itemprop="description" content="{nicknames[username]}的知乎文章和回答索引">
    """
        + """
        <style>
            body { max-width: 800px; margin: 0 auto; padding: 20px; }
            .item { margin: 10px 0; }
            .votes { color: #666; font-size: 0.9em; }
            .created_time { color: #999; font-size: 0.9em; }
            .censored { background-color: #ffeb3b; }

            /* Tab styles */
            .tabs { margin-bottom: 20px; }
            .tab-button {
                padding: 10px 20px;
                border: none;
                background: #f0f0f0;
                cursor: pointer;
                font-size: 16px;
            }
            .tab-button.active {
                background: #007bff;
                color: white;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
        </style>
        <script>
            function openTab(evt, tabName) {
                var tabContents = document.getElementsByClassName("tab-content");
                for (var i = 0; i < tabContents.length; i++) {
                    tabContents[i].classList.remove("active");
                }
                var tabButtons = document.getElementsByClassName("tab-button");
                for (var i = 0; i < tabButtons.length; i++) {
                    tabButtons[i].classList.remove("active");
                }
                document.getElementById(tabName).classList.add("active");
                evt.currentTarget.classList.add("active");
            }
        </script>
    </head>
    <body>
    """
        + f"""
        <h1>{nicknames[username]}的知乎索引</h1>
        <div class="tabs">
            <button class="tab-button active" onclick="openTab(event, 'answers-tab')">回答 ({len(answers)})</button>
            <button class="tab-button" onclick="openTab(event, 'articles-tab')">文章 ({len(articles)})</button>
        </div>

        <div id="answers-tab" class="tab-content active">
            <h2>回答</h2>
    """
    )

    # Add answers
    for answer in answers:
        question_title = (
            answer["question"]["title"]
            if "question" in answer and "title" in answer["question"]
            else "Untitled"
        )
        is_censored = answer.get("censored", False)
        censored_class = "censored" if is_censored else ""
        censored_text = " (censored)" if is_censored else ""

        html_content += f"""
            <div class="item">
                <a href="https://www.fxzhihu.com/answer/{answer['file_stem']}" class="{censored_class}">{question_title}{censored_text}</a>
                <span class="votes">({answer['voteup_count']} 赞同)</span>
                <span class="created_time">({datetime.fromtimestamp(answer['created_time']).strftime('%Y-%m-%d')})</span>
            </div>
    """

    html_content += """
        </div>
        <div id="articles-tab" class="tab-content">
            <h2>文章</h2>
    """

    # Add articles
    for article in articles:
        is_censored = article.get("censored", False)
        censored_class = "censored" if is_censored else ""
        censored_text = " (censored)" if is_censored else ""
        html_content += f"""
            <div class="item">
                <a href="https://zhuanlan.fxzhihu.com/p/{article['file_stem']}" class="{censored_class}">{article['title']}{censored_text}</a>
                <span class="votes">({article['voteup_count']} 赞同)</span>
                <span class="created_time">({datetime.fromtimestamp(article['created']).strftime('%Y-%m-%d')})</span>
            </div>
    """

    html_content += """
        </div>
        <hr>
        <p><a href="./">← 返回目录</a></p>
    </body>
    </html>
    """

    Path(f"./docs").mkdir(exist_ok=True)

    # Write the HTML file
    with open(f"./docs/{username}.html", "w", encoding="utf-8") as f:
        f.write(html_content)


def generate_index_html():
    """Generate index.html as the entry point for ZhiHuLegend website"""
    index_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>ZhiHu Legend</title>
        <meta property="og:type" content="website">
        <meta property="og:title" content="知乎封神榜">
        <meta property="og:site_name" content="ZhiHu Legend">
        <meta property="og:url" content="https://l-m-sherlock.github.io/ZhiHuLegend/">
        <meta name="description" property="og:description" content="ZhiHu Legend - 知乎封神榜">
        <meta name="google-site-verification" content="U7ZAFUgGNK60mmMqaRygg5vy-k8pwbPbDXNjDCu7Xk" />
        <meta property="twitter:card" content="summary">
        <meta name="twitter:title" property="og:title" itemprop="name" content="知乎封神榜">
        <meta name="twitter:description" property="og:description" itemprop="description" content="ZhiHu Legend - 知乎封神榜">
        <style>
            body { max-width: 800px; margin: 0 auto; padding: 20px; }
            .user-list { margin: 20px 0; }
            .user-item { margin: 10px 0; }
            .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
        </style>
    </head>
    <body>
        <h1>知乎封神榜</h1>
        <p>
            <a href="https://github.com/l-m-sherlock/ZhiHuLegend">
                <img src="https://img.shields.io/github/stars/l-m-sherlock/ZhiHuLegend?style=social" alt="GitHub stars">
            </a>
        </p>
        <div class="user-list">
    """

    # Add links to each user's summary page
    for username, nickname in nicknames.items():
        index_content += f"""
            <div class="user-item">
                <a href="{username}.html">{nickname}的知乎索引</a>
            </div>
        """

    index_content += """
        </div>
        <div class="footer">
            <div class="links-section">
                <h3>友情链接</h3>
                <a href="https://l-m-sherlock.github.io/ZhiHuArchive/" target="_blank">Thoughts Memo 和叶峻峣的知乎文章和回答备份目录</a>
            </div>
        </div>
    </body>
    </html>
    """

    # Write the index.html file
    with open("./docs/index.html", "w", encoding="utf-8") as f:
        f.write(index_content)


for username in nicknames:
    generate_summary(username)

# Generate index.html after all summary pages are created
generate_index_html()
