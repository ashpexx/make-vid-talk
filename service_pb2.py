# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: service.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rservice.proto\x12\x05video\"\x07\n\x05\x45mpty\"1\n\x0eStatusResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"-\n\rUploadRequest\x12\r\n\x05video\x18\x01 \x01(\x0c\x12\r\n\x05\x61udio\x18\x02 \x01(\x0c\"a\n\x0eUploadResponse\x12\x11\n\tvideo_url\x18\x01 \x01(\t\x12\x11\n\taudio_url\x18\x02 \x01(\t\x12\x12\n\nresult_url\x18\x03 \x01(\t\x12\x15\n\rthumbnail_url\x18\x04 \x01(\t\"\x1c\n\rDeleteRequest\x12\x0b\n\x03key\x18\x01 \x01(\t2\xb7\x01\n\x0cVideoService\x12\x33\n\x0cServerActive\x12\x0c.video.Empty\x1a\x15.video.StatusResponse\x12\x37\n\x06Upload\x12\x14.video.UploadRequest\x1a\x15.video.UploadResponse(\x01\x12\x39\n\nDeleteFile\x12\x14.video.DeleteRequest\x1a\x15.video.StatusResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_EMPTY']._serialized_start=24
  _globals['_EMPTY']._serialized_end=31
  _globals['_STATUSRESPONSE']._serialized_start=33
  _globals['_STATUSRESPONSE']._serialized_end=82
  _globals['_UPLOADREQUEST']._serialized_start=84
  _globals['_UPLOADREQUEST']._serialized_end=129
  _globals['_UPLOADRESPONSE']._serialized_start=131
  _globals['_UPLOADRESPONSE']._serialized_end=228
  _globals['_DELETEREQUEST']._serialized_start=230
  _globals['_DELETEREQUEST']._serialized_end=258
  _globals['_VIDEOSERVICE']._serialized_start=261
  _globals['_VIDEOSERVICE']._serialized_end=444
# @@protoc_insertion_point(module_scope)
