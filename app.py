import os, boto3

DIST_ID       = os.environ['DIST_ID']
SORRY_PATTERN = os.environ.get('SORRY_PATTERN', '*')

cf   = boto3.client('cloudfront', region_name='us-east-1')

def lambda_handler(event, context):
    # 1. 現行設定取得
    res   = cf.get_distribution_config(Id=DIST_ID)
    cfg   = res['DistributionConfig']
    etag  = res['ETag']

    # 2. CacheBehavior を抽出
    items = cfg.get('CacheBehaviors', {}).get('Items', [])

    # 3. 「Sorry」と「その他」に分離
    sorry  = None
    others = []
    for b in items:
        if b['PathPattern'] == SORRY_PATTERN:
            sorry = b
        else:
            others.append(b)

    # 4. Priority を 0,1,2,3… に振り直し
    priority = 0
    if sorry:
        sorry['Priority'] = priority
        priority += 1

    # 元の順序を保ったまま残りに連番を振る
    for b in sorted(others, key=lambda x: x['Priority']):
        b['Priority'] = priority
        priority += 1

    # 5. 更新
    cf.update_distribution(
        Id=DIST_ID,
        DistributionConfig=cfg,
        IfMatch=etag
    )

    return {"message": "closed (sorry-page enabled)"}
