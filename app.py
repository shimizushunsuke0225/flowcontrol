import os, boto3

DIST_ID       = os.environ['DIST_ID']
SORRY_PATTERN = os.environ.get('SORRY_PATTERN', '*')
SORRY_PRIO    = 0          # 閉塞時に与える優先度

# CloudFrontはグローバルサービスなので、us-east-1リージョンを使用する必要がある
cf = boto3.client('cloudfront', region_name='us-east-1')

def lambda_handler(event, context):
    # 1. 現行設定と ETag
    res   = cf.get_distribution_config(Id=DIST_ID)
    cfg   = res['DistributionConfig']
    etag  = res['ETag']

    # 2. CacheBehavior の Priority を並べ替え
    items = cfg.get('CacheBehaviors', {}).get('Items', [])
    for beh in items:
        if beh['PathPattern'] == SORRY_PATTERN:
            beh['Priority'] = SORRY_PRIO      # Sorry を 0 番へ
        else:
            if beh['Priority'] <= SORRY_PRIO: # 衝突回避
                beh['Priority'] += 1          # 0→1,1→2 … と後ろへ

    # 3. 更新
    cf.update_distribution(
        Id=DIST_ID,
        DistributionConfig=cfg,
        IfMatch=etag
    )
    return {"message": "closed (sorry-page enabled)"}