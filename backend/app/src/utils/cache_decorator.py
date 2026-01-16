import functools
import hashlib
from typing import Callable, Any
from .redis_client import redis_client
from .logger import app_logger
from datetime import timedelta


def cache_result(
    ttl: int = 300,
    key_prefix: str = "",
    include_args: bool = True,
    exclude_args: list = None,
):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            cache_key_parts = [key_prefix or func.__name__]

            if include_args:
                arg_names = func.__code__.co_varnames[: func.__code__.co_argcount]

                start_idx = 0
                if (
                    args
                    and hasattr(args[0], "__class__")
                    and func.__name__ in dir(args[0].__class__)
                ):
                    start_idx = 1

                args_part = []
                for i in range(start_idx, len(args)):
                    arg = args[i]
                    if i < len(arg_names):
                        arg_name = arg_names[i]
                        if exclude_args and arg_name in exclude_args:
                            continue
                        args_part.append(f"{arg_name}:{arg}")
                    else:
                        args_part.append(str(arg))

                kwargs_part = []
                for k, v in kwargs.items():
                    if exclude_args and k in exclude_args:
                        continue
                    kwargs_part.append(f"{k}:{v}")

                all_args = args_part + sorted(kwargs_part)
                if all_args:
                    args_str = "&".join(all_args)
                    args_hash = hashlib.md5(args_str.encode("utf-8")).hexdigest()
                    cache_key_parts.append(args_hash)

            cache_key = ":".join(cache_key_parts)

            app_logger.info(f"Cache key generated: {cache_key}")
            app_logger.info(f"Args: {args}, Kwargs: {kwargs}")

            try:
                cached_result = await redis_client.get(cache_key)
                if cached_result is not None:
                    app_logger.info(f"Cache HIT for key: {cache_key}")
                    return cached_result

                result = await func(*args, **kwargs)

                cache_success = await redis_client.set(
                    cache_key, result, expire=timedelta(seconds=ttl)  # TTL here!
                )
                if cache_success:
                    app_logger.info(f"Cache SET for key: {cache_key}, TTL: {ttl}s")
                else:
                    app_logger.warning(f"Failed to cache result for key: {cache_key}")

                return result

            except Exception as e:
                app_logger.error(f"Cache operation failed: {e}")
                try:
                    return await func(*args, **kwargs)
                except Exception as func_error:
                    app_logger.error(f"Function execution failed: {func_error}")
                    raise

        return wrapper

    return decorator


async def invalidate_cache(pattern: str):
    try:
        success = await redis_client.flush_pattern(pattern)
        if success:
            app_logger.info(f"Cache invalidated for pattern: {pattern}")
        else:
            app_logger.warning(
                f"Cache invalidation returned False for pattern: {pattern}"
            )
        return success
    except Exception as e:
        app_logger.error(f"Cache invalidation failed: {e}")
        return False


async def invalidate_function_cache(function_name: str, arg_value: str = None):
    if arg_value:
        arg_hash = hashlib.md5(arg_value.encode()).hexdigest()
        pattern = f"{function_name}:*{arg_hash}*"
    else:
        pattern = f"{function_name}:*"

    return await invalidate_cache(pattern)
