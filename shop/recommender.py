import redis
from django.conf import settings
from .models import Product

# Initialize Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

class Recommender:
    def __init__(self):
        self.redis = redis_client

    def get_product_key(self, id):
        """
        Generate a Redis key for the product.
        """
        return f'product:{id} purchased with'
    
    def products_bought(self, products):
        """
        Record that a product was bought together with another product.
        """
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # get the other products bought with each product
                if product_id != with_id:
                # increment the count of products bought together
                    self.redis.zincrby(self.get_product_key(with_id), 1, product_id)

    def suggest_products_for(self, products, max_results=6):
        """
        Suggest products based on the products bought together.
        """
        product_ids = [p.id for p in products]
        if len(products) == 1:
            # If only one product, suggest similar products
            suggestions = self.redis.zrange(self.get_product_key(product_ids[0]), 0, -1, desc=True)[:max_results]
        else:
            # generate a temporary key
            flat_ids = ''.join([str(id) for id in product_ids])
            temp_key = f'temp_suggestions:{flat_ids}'
            # multiple products, combine scores of all products
            # store the resulting sorted set in a temporary key
            keys = [self.get_product_key(id) for id in product_ids]
            self.redis.zunionstore(
                temp_key,
                keys,
                # aggregate='SUM'
            )
            # remove ids for the products the recommendation is for
            self.redis.zrem(temp_key, *product_ids)
            # get the product ids by their score, descendant sort
            suggestions = self.redis.zrange(temp_key, 0, -1, desc=True)[:max_results]
            # remove the temporary key
            self.redis.delete(temp_key)
        suggested_product_ids = [int(id) for id in suggestions]
        # get suggested products and sort by order of appearance
        suggested_products = list(Product.objects.filter(id__in=suggested_product_ids))
        suggested_products.sort(key=lambda x: suggested_product_ids.index(x.id))
        return suggested_products

    def clear_purchases(self):
        for id in Product.objects.values_list('id', flat=True):
            self.redis.delete(self.get_product_key(id))

   
