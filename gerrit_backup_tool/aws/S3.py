
"""S3 Class."""

import socket
import os

try:
    import boto
except ImportError:
    raise ImportError("Python module 'boto' needs to be installed on target box: %s" %
                      socket.getfqdn())

import utils
import log


class S3(object):
    """S3."""

    def __init__(self, access_key, secret_key, bucket):
        """Init."""
        super(S3, self).__init__()
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket

        self.encrypt_files = False
        self.content_type = ''

    def get_connection(self):
        """Open S3 Connection."""
        # boto.set_stream_logger('boto')  # DEBUG

        conn = boto.connect_s3(self.access_key,
                               self.secret_key,
                               is_secure=True)

        return conn

    def list_bucket_keys(self):
        """List S3 buckets."""
        conn = self.get_connection()
        s3_bucket = conn.get_bucket(self.bucket)

        log.print_log("Listing S3 Bucket Files: %s" % s3_bucket.name)

        for key in s3_bucket.list(delimiter="/"):
            log.print_log(key.name)

    def get_key(self, s3_key):
        """Get S3 key."""
        conn = self.get_connection()
        s3_bucket = conn.get_bucket(self.bucket)
        # log.print_log("Getting S3 file: %s" % (s3_key))
        key = s3_bucket.get_key(s3_key)
        if key is None:
            raise RuntimeError("ERROR: Bucket Key not found: %s" % s3_key)

        return key

    def get_all_bucket_versions(self, prefix=''):
        """Get bucket version list."""
        conn = self.get_connection()
        s3_bucket = conn.get_bucket(self.bucket)
        return s3_bucket.list_versions(prefix=prefix)

    def get_key_versions(self, s3_key):
        """Get key version list."""
        versions = []
        for version in self.get_all_bucket_versions(prefix=s3_key):
            versions.append(version.version_id)

        return versions

    def get_latest_versions(self, s3_key):
        """Get key latest version list."""
        key = self.get_key(s3_key)
        return key.version_id

    def upload_file(self, s3_key, file_path):
        """Upload a files to S3."""
        if not os.path.exists(file_path):
            raise RuntimeError("ERROR: File not found: %s" % file_path)

        log.print_log("Uploading file: %s" % file_path)

        conn = self.get_connection()
        s3_bucket = conn.get_bucket(self.bucket)

        file_size = os.stat(file_path).st_size
        file_human_size = utils.human_size(file_size)
        log.print_log("Uploading to S3 key: %s (%s)" % (s3_key, file_human_size))

        key = s3_bucket.new_key(s3_key)

        if self.content_type:
            key.set_metadata('Content-Type', self.content_type)

        if self.encrypt_files is True:
            key.set_metadata('x-amz-meta-s3tools-gpgenc', 'gpg')  # FYI: For s3cmd

        bytes_written = key.set_contents_from_filename(file_path, encrypt_key=True)

        if bytes_written != file_size:
            msg = "ERROR: Mismatch in bytes synced to S3 bucket and local file: " \
                  "{0} != {1}".format(bytes_written, file_size)
            raise RuntimeError(msg)

        # key.set_acl('private')

    def download_file(self, s3_key, to_file, file_ext=''):
        """Download a files from S3."""
        file_ext = file_ext.lower()
        s3_key = s3_key + file_ext
        key = self.get_key(s3_key)

        file_extension = os.path.splitext(to_file)[1]
        if file_extension.lower() != file_ext and \
           self.encrypt_files is True:
            to_file += '.gpg'

        log.print_log("  Downloading To: %s" % to_file)
        key.get_contents_to_filename(to_file)

        if not os.path.exists(to_file):
            raise RuntimeError("ERROR: File not download: %s" % to_file)
