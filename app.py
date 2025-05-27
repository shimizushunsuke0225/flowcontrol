import os
import boto3
import json
import time
import logging

# ロガー設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数から設定を取得
DIST_ID = os.environ.get('DIST_ID')
MAINT_PATTERN = os.environ.get('MAINT_PATTERN')
TARGET_PRIORITY = int(os.environ.get('TARGET_PRIORITY', '0'))

# CloudFrontクライアント
cloudfront = boto3.client('cloudfront')

def lambda_handler(event, context):
    """
    CloudFrontのビヘイビア優先順位を変更するLambda関数
    
    環境変数:
        DIST_ID: CloudFront Distribution ID
        MAINT_PATTERN: メンテナンス用のPathPattern
        TARGET_PRIORITY: 設定する優先度 (0=メンテナンス開始, 1000=メンテナンス終了)
    """
    logger.info(f"Starting behavior priority switch for distribution {DIST_ID}")
    logger.info(f"Maintenance pattern: {MAINT_PATTERN}, Target priority: {TARGET_PRIORITY}")
    
    # 最大リトライ回数
    max_retries = 3
    retry_count = 0
    backoff_time = 1  # 初期バックオフ時間（秒）
    
    while retry_count < max_retries:
        try:
            # ディストリビューション設定を取得
            response = cloudfront.get_distribution_config(Id=DIST_ID)
            config = response['DistributionConfig']
            etag = response['ETag']
            
            logger.info(f"Got distribution config with ETag: {etag}")
            
            # ビヘイビアが存在するか確認
            if 'CacheBehaviors' not in config or 'Items' not in config['CacheBehaviors']:
                logger.warning("No cache behaviors found in distribution")
                return {
                    'statusCode': 400,
                    'body': json.dumps('No cache behaviors found in distribution')
                }
            
            # ビヘイビアリストを取得
            behaviors = config['CacheBehaviors']['Items']
            
            # メンテナンス用ビヘイビアを探して優先度を変更
            maint_behavior_found = False
            for behavior in behaviors:
                if behavior['PathPattern'] == MAINT_PATTERN:
                    logger.info(f"Found maintenance behavior with pattern {MAINT_PATTERN}")
                    logger.info(f"Changing priority from {behavior['Priority']} to {TARGET_PRIORITY}")
                    behavior['Priority'] = TARGET_PRIORITY
                    maint_behavior_found = True
                else:
                    # 衝突回避: TARGET_PRIORITYと重なったら+10
                    if int(behavior['Priority']) == TARGET_PRIORITY:
                        logger.info(f"Conflict detected for behavior {behavior['PathPattern']}, adjusting priority")
                        behavior['Priority'] = TARGET_PRIORITY + 10
            
            if not maint_behavior_found:
                logger.warning(f"No behavior with pattern {MAINT_PATTERN} found")
                return {
                    'statusCode': 404,
                    'body': json.dumps(f"No behavior with pattern {MAINT_PATTERN} found")
                }
            
            # 更新を適用
            logger.info("Updating distribution with new priorities")
            cloudfront.update_distribution(
                Id=DIST_ID,
                DistributionConfig=config,
                IfMatch=etag
            )
            
            logger.info("Distribution update initiated successfully")
            return {
                'statusCode': 200,
                'body': json.dumps('CloudFront behavior priorities updated successfully')
            }
            
        except cloudfront.exceptions.PreconditionFailed as e:
            # ETag不一致エラー - 指数バックオフで再試行
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"ETag mismatch, retrying in {backoff_time} seconds (attempt {retry_count}/{max_retries})")
                time.sleep(backoff_time)
                backoff_time *= 2  # 指数バックオフ
            else:
                logger.error("Maximum retries reached for ETag mismatch")
                raise
                
        except Exception as e:
            logger.error(f"Error updating distribution: {str(e)}")
            raise