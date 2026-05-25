from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import csv, io, boto3, os                          
from botocore.exceptions import ClientError, NoCredentialsError

load_dotenv()
print(os.environ.get("S3_BUCKET", "NOT FOUND"))
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-in-production")

S3_BUCKET = os.environ.get("S3_BUCKET", "")
S3_PREFIX = os.environ.get("S3_PREFIX", "processed/")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")

@app.route("/")
def index():
    files = list_processed_files()
    return render_template("index.html", files=files, s3_configured=bool(S3_BUCKET))




def parse_csv(content: str) -> list[dict]:
    rows = []
    reader = csv.reader(io.StringIO(content))
    for i, row in enumerate(reader, start=1):                                                                   
      if len(row) >= 3:                                                                                       
          rows.append({
              "row_num": i,
              "sku_id": row[0].strip(),
              "product_name": row[1].strip(),
              "price": row[2].strip()
          })

    return rows
    
def list_processed_files() -> list[dict]:
    if not S3_BUCKET:
        return []
    try:
        s3 = boto3.client('s3', region_name=AWS_REGION)
        resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_PREFIX)
        files = []
        for obj in resp.get("Contents", []):
            name = obj["Key"].removeprefix(S3_PREFIX)
            if name:
                files.append({
                    "key": obj["Key"],
                    "name": name,
                    "size_kb": round(obj["Size"] / 1024, 1),
                    "last_modified": obj["LastModified"].strftime("%Y-%m-%d %H:%M UTC"),
                })
        return sorted(files, key=lambda f: f["last_modified"], reverse=True)
    except (ClientError, NoCredentialsError):
        return []


def upload_to_s3(content: str, filename: str) -> tuple[bool, str]:
    if not S3_BUCKET:
        return False, "S3_BUCKET environment variable not set"
    try:
        s3 = boto3.client('s3',region_name=AWS_REGION)
        raw_bytes = content.encode("utf-8")
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=S3_PREFIX + filename,
            Body=raw_bytes,
            ContentType="text/csv",
        )
        return True, f"s3://{S3_BUCKET}/{S3_PREFIX}{filename}"
    
    except NoCredentialsError:
      return False, "AWS credentials not configured"
    except ClientError as exc:
      return False, f"S3 error: {exc}"       



@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if file is None:
        flash("No file part in the request", "error")
        return redirect(url_for("index"))
    
    if not file.filename:
        flash("No file selected.", "error")
        return redirect(url_for("index"))
    
    if "." not in file.filename or file.filename.rsplit(".", 1)[1].lower() != "csv":
        flash("Only CSV files are allowed.", "error")
        return redirect(url_for("index"))
 
    # content = file.read().decode("utf-8", errors="replace")
    # rows = parse_csv(content)
    # return render_template("result.html", rows=rows, row_count=len(rows))

    content = file.read().decode("utf-8", errors="replace")
    filename = secure_filename(file.filename)
    rows = parse_csv(content)
    s3_ok, s3_msg = upload_to_s3(content, filename)
    return render_template("result.html", rows=rows, row_count=len(rows), s3_ok=s3_ok, s3_msg=s3_msg)

@app.route("/health")                                                                                       
def health():                                                                                               
    return jsonify(status="ok"), 200 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)