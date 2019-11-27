from typing import Callable, Type, TypeVar, Any, Iterable

from datapipelines import DataSink, PipelineContext

from google.cloud import storage
from google.cloud.exceptions import Forbidden, NotFound
from google.cloud.storage import Bucket, Client as GCSClient

from . import uniquekeys
from ..dto.match import MatchDto, TimelineDto

# try:
#     import ujson as json
# except ImportError:
#     import json
#
#     json.decode = json.loads

T = TypeVar("T")


class GoogleCloudStorage(DataSink):
    def __init__(self, project_id, region) -> None:
        self._client = GCSClient(project_id, region)

    @DataSink.dispatch
    def put(self, type: Type[T], item: T, context: PipelineContext = None) -> None:
        pass

    @DataSink.dispatch
    def put_many(self, type: Type[T], items: Iterable[T], context: PipelineContext = None) -> None:
        pass

    # Match
    @put.register(MatchDto)
    def put_match(self, item: MatchDto) -> None:
        print('gcs put match dto')
        self._client.put(MatchDto, item, uniquekeys.for_match_dto)

    # Timeline
    @put.register(TimelineDto)
    def put_timeline(self, item: TimelineDto) -> None:
        self._client.put(TimelineDto, item, uniquekeys.for_match_timeline_dto)


class GCSClient(object):
    def __init__(self, project_id, region) -> None:
        self._client = storage.Client()
        self._project_id = project_id
        self._region = region
        self._buckets = {
            MatchDto: self.get_bucket(f'match-{self._region}-x'),
            TimelineDto: self.get_bucket(f'timeline-{self._region}-x')
        }

    def get_bucket(self, bucket_name):
        try:
            bucket = self._client.get_bucket(bucket_name)
            print(f'got bucket {bucket_name} in {self._project_id} {self._region}')
        except (Forbidden, NotFound):
            bucket = self.create_bucket(bucket_name)
        return bucket

    def create_bucket(self, name):
        print(f'creating bucket {name} in {self._project_id} {self._region}')
        bucket = Bucket(self._client, name)
        bucket.create(self._client, self._project_id, self._region)
        return bucket

    def put(self, type: Type[T], item: T, key_function: Callable[[T], Any], ) -> None:
        print('storing {key_function(item)} in {type} bucket')
        blob = self._buckets[type].blob(key_function(item))
        print(f'dumping object of type {type(item)}')
        blob.upload_from_string(item)
