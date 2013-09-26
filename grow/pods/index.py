import collections
import hashlib
import yaml


class Index(object):
  BASENAME = '.growindex'
  Diff = collections.namedtuple('Diff', ['adds', 'edits', 'deletes', 'nochanges'])

  def __init__(self, paths_to_shas=None):
    if paths_to_shas is None:
      paths_to_shas = {}
    self.paths_to_shas = paths_to_shas

  def __contains__(self, key):
    return key in self.paths_to_shas

  def __getitem__(self, key):
    return self.paths_to_shas[key]

  def __delitem__(self, key):
    del self.paths_to_shas[key]

  def iteritems(self):
    return self.paths_to_shas.iteritems()

  def update(self, paths_to_contents):
    self.paths_to_shas = {}
    for pod_path, contents in paths_to_contents.iteritems():
      pod_path = '/' + pod_path.lstrip('/')
      m = hashlib.sha1()
      if isinstance(contents, unicode):
        contents = contents.encode('utf-8')
      m.update(contents)
      self.paths_to_shas[pod_path] = m.hexdigest()
    return self.paths_to_shas

  def diff(self, theirs):
    """Shows a diff of what will happen after applying yours to theirs."""
    diff = Index.Diff(adds=[], edits=[], deletes=[], nochanges=[])

    for path, sha in self.iteritems():
      if path in theirs:
        if self[path] == theirs[path]:
          diff.nochanges.append(path)
        else:
          diff.edits.append(path)
        del theirs[path]
      else:
        diff.adds.append(path)

    for path, sha in theirs.iteritems():
      diff.deletes.append(path)

    return diff

  def to_yaml(self):
    return yaml.dump(self.paths_to_shas, default_flow_style=False)

  @classmethod
  def from_yaml(cls, yaml_string):
    return cls(yaml.load(yaml_string))
