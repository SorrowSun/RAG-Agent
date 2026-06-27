```
import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)
```

------

# 二、String（字符串）操作 ⭐最常用

```
redis_client.set(name, value)
redis_client.get(name)

redis_client.setex(name, time, value)   # 设置过期时间
redis_client.mset(dict)                 # 批量设置
redis_client.mget(keys)                 # 批量获取

redis_client.incr(name)
redis_client.decr(name)
redis_client.append(name, value)
```

------

# 三、Key（键管理）

```
redis_client.exists(name)
redis_client.delete(name)
redis_client.expire(name, time)
redis_client.ttl(name)

redis_client.keys("*")     # 模糊匹配（慎用，生产很慢）
redis_client.type(name)
```

------

# 四、Hash（哈希，类似 JSON）

```
redis_client.hset(name, key, value)
redis_client.hget(name, key)
redis_client.hgetall(name)

redis_client.hmset(name, mapping)   # 批量（新版不推荐但还能用）
redis_client.hmget(name, keys)

redis_client.hdel(name, key)
redis_client.hexists(name, key)
redis_client.hkeys(name)
redis_client.hvals(name)
```

------

# 五、List（列表）

```
redis_client.lpush(name, value)
redis_client.rpush(name, value)

redis_client.lpop(name)
redis_client.rpop(name)

redis_client.lrange(name, start, end)
redis_client.llen(name)

redis_client.lindex(name, index)
redis_client.lset(name, index, value)
```

------

# 六、Set（集合）

```
redis_client.sadd(name, value)
redis_client.srem(name, value)

redis_client.smembers(name)
redis_client.scard(name)

redis_client.sismember(name, value)
redis_client.spop(name)
```

------

# 七、Sorted Set（有序集合 ZSET）

```
redis_client.zadd(name, mapping)   # {"member": score}

redis_client.zrange(name, start, end)
redis_client.zrevrange(name, start, end)

redis_client.zscore(name, member)
redis_client.zrank(name, member)

redis_client.zcard(name)
redis_client.zrem(name, member)
```

------

# 八、事务 / pipeline（性能优化🔥）

```
pipe = redis_client.pipeline()

pipe.set("a", 1)
pipe.set("b", 2)
pipe.execute()
```

------

# 九、发布订阅（Pub/Sub）

```
pubsub = redis_client.pubsub()

pubsub.subscribe("channel")

redis_client.publish("channel", "hello")
```

------

# 十、分布式锁（很重要🔥）

```
lock = redis_client.lock("my_lock", timeout=10)

lock.acquire()
lock.release()
```

------

# 十一、其他常用能力

```
redis_client.flushdb()   # 清空当前库（危险）
redis_client.flushall()  # 清空所有库（更危险）

redis_client.info()      # Redis 状态信息
redis_client.dbsize()    # key数量
```