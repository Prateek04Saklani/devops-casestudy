FROM python:3.11-slim   
WORKDIR /app
COPY requirements.txt .                                                                                     
RUN pip install --no-cache-dir -r requirements.txt 
COPY . .

RUN mkdir -p /shared/static && \                                                                            
      groupadd -r appgroup && \                                                                               
      useradd -r -g appgroup -d / -s /sbin/nologin appuser  && \                                                                     
      chown -R appuser:appgroup /app /shared/static && \                                                      
      chmod +x /app/entrypoint.sh 

ENV HOME=/tmp
USER appuser

EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]