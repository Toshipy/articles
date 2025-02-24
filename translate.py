import os
from pathlib import Path
from dotenv import load_dotenv
import deepl
from typing import Dict, Tuple, Any
import frontmatter
load_dotenv()

class DeepLTranslator:
  def __init__(self):
    self.translator = deepl.Translator(os.getenv("DEEPL_API_KEY"))

  def translate_text(self, text: str) -> str:
    """DeepLでテキストを翻訳する"""
    try:
      result = self.translator.translate_text(text, target_lang="EN-US")
      return str(result)
    except Exception as e:
      print(f"翻訳に失敗しました: {e}")
      raise

  def translate_frontmatter(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Frontmatterを翻訳する"""
    translated_metadata = {}
    try:
      # Titleは必須
      translated_metadata["title"] = self.translate_text(metadata["title"])
      # Descriptionがあれば翻訳
      if "description" in metadata:
        translated_metadata["description"] = self.translate_text(metadata["description"])
      # Tagsはそのまま
      if "tags" in metadata:
        translated_metadata["tags"] = metadata["tags"]
      # PublishedAtはそのまま
      if "published" in metadata:
        translated_metadata["published"] = metadata["published"]
      return translated_metadata
    except Exception as e:
      print(f"翻訳に失敗しました: {e}")
      raise

class ArticleProcessor:
  def __init__(self):
    self.translator = DeepLTranslator()

  def process_article(self, src_path: Path) -> Tuple[Dict[str, Any], str]:
    """記事を翻訳して保存する"""
    print(f"Processing {src_path}...")
    
    # 記事を読み込み
    post = frontmatter.load(str(src_path))
    
    # frontmatterを翻訳
    translated_metadata = self.translator.translate_frontmatter(post.metadata)
    
    # 記事の内容を翻訳
    print("Translating content with DeepL...")
    translated_content = self.translator.translate_text(post.content)
    print("Translation completed.")
    
    return translated_metadata, translated_content
  
  def save_article(self, dest_path: str, frontmatter_data: Dict[str, Any], content: str):
    """翻訳した記事を保存する"""
    print(f"Saving translated article to {dest_path}...")
    
    # 保存先のディレクトリがなければ作成
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # dev.to用のフロントマターに変換
    devto_frontmatter = {
      "title": frontmatter_data["title"],
      "body_markdown": content,
      "published": frontmatter_data["published"],
      "tags": frontmatter_data["tags"]
    }
    # 記事を保存
    post = frontmatter.Post(content, **frontmatter_data)
    with open(dest_path, "wb") as f:
        frontmatter.dump(post, f)
    print(f"Saved translated article to: {dest_path}")
      
def main():
    processor = ArticleProcessor()
    
    # articles/配下のMarkdownファイルを処理
    articles_dir = Path("articles")
    translate_dir = Path("translate")
    
    for src_path in articles_dir.glob("*.md"):
        try:
            # 出力パスを設定
            dest_path = translate_dir / src_path.name
            
            # 既に翻訳済みかチェック
            if dest_path.exists():
                print(f"Translation already exists: {dest_path}")
                continue
            
            # 記事を処理
            frontmatter_data, translated_content = processor.process_article(src_path)
            
            # 保存
            processor.save_article(dest_path, frontmatter_data, translated_content)
            
        except Exception as e:
            print(f"Error processing {src_path}: {e}")

if __name__ == "__main__":
    main()
