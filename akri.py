#!/usr/bin/env python
"""Because I cannot remember riak..
* can make most logic generic with path selector.
"""
import sys,os
import urllib2                  # xx banish
import urllib                   # can requests quote?
import json
from subprocess import Popen, PIPE
import requests
import baker

def bucket_url(**kw):
    return "http://{host}:8098/buckets/{bucket}".format(**kw)

api_map=dict(
    bucket_props=("http://{host}:8098/buckets/{bucket}/props", "bucket properties"),
)

def api_url(api, **kw):
    urlt,doc=api_map[api]
    url=urlt.format(**kw)
    return url

def _get(api, **kw):
    url=api_url(api, **kw)
    if kw.get('verbose'):
        print >>sys.stderr, url
    r=urllib2.urlopen(url)      # xx convert to requests.
    return r.read()

@baker.command
def keys(bucket, host='localhost', port=8098):
    """stream keys
    Could take forever for a large bucket.
    curl -s http://{host}:8098/buckets/{bucket}/keys?keys=stream
    """
    url="http://{host}:8098/buckets/{bucket}/keys?keys=stream".format(**locals())
    print >>sys.stderr, url
    # xx response is undelimited concatnation of jsons: {..}{..}{..}
    #    Need an incremental json parser to deal with this.
    p=Popen("curl -s {url} | jq -M -c .".format(url=url), shell=True, stdout=PIPE)
    for line in p.stdout.readlines():
        chunk=json.loads(line)
        for key in chunk['keys']:
            print key
    p.wait()

@baker.command
def key_range():
    """
    curl -s 'http://{host}:8098/buckets/{bucket}/index/$key/{start}/{end} 
    note: must be url-encoded.
    """
    IMPLEMENT_ME

@baker.command
def vals(bucket, host='localhost', port=8098, verbose=False):
    """get the value for the keys"""
    # xx refactor
    burl=bucket_url(**locals())
    for key in sys.stdin.readlines():
        key=key.strip('\n')
        url=os.path.join(burl, 'keys', urllib.quote(key, ""))
        r=requests.get(url)
        print r.content

@baker.command
def delete(bucket, host='localhost', port=8098, verbose=False, dryrun=True):
    """delete keys read from stdin"""
    if dryrun:
        verbose=True
    # xx is there an aggregated delete method?
    burl=bucket_url(**locals())
    for key in sys.stdin.readlines():
        key=key.strip('\n')
        url=os.path.join(burl, 'keys', urllib.quote(key, ""))
        if verbose:
            print 'DELETE', url
        if not dryrun:
            r=requests.delete(url)
            print r.status_code, url

@baker.command
def bucket_props(bucket, host='localhost', port=8098):
    """bucket properties
    http://{host}:8098/buckets/{bucket}/props
    """
    print _get('bucket_props', **locals())

# xx namedtuple..
conflict_resolution_policy_def=dict(
    #policy       last_write_wins allow_mult desc
    stomp=        (True,   False,             "just clobber."),
    most_recent=  (False,  False,             "pick most recent sibling. default."),
    siblings=     (False,  True,              "let application handle siblings."),
    undefined=    (True,   True,              "do not use.")
)

@baker.command
def conflict_resolution_policy(bucket, host='localhost', port=8098, verbose=False):
    """print the current policy in effect for the bucket.
    """
    props=json.loads(_get('bucket_props', **locals()))
    last_write_wins_allow_mult=props['props']['last_write_wins'], props['props']['allow_mult']
    
    inverted=dict( (v[:2], ((k,)+v[2:])) for k,v in conflict_resolution_policy_def.items() )

    bucket_url="http://{host}:8098/buckets/{bucket}".format(**locals())
    policy_tpl=inverted[last_write_wins_allow_mult]
    print '\t'.join((bucket_url,)+policy_tpl)

@baker.command
def conflict_resolution_policy_update(bucket, policy, host='localhost', port=8098, verbose=False, dryrun=False):
    """set the coflict resolution policy
    curl -XPUT \
         -H "Content-Type: application/json" \
         -d '{"props":{"allow_mult":false, ..}}' \
         http://{host}:{port}/riak/{bucket}
    """
    if dryrun:
        verbose=True

    url=api_url('bucket_props', **locals())
    last_write_wins,allow_mult,desc=conflict_resolution_policy_def[policy]
    props_update_d=dict(props=dict(last_write_wins=last_write_wins, allow_mult=allow_mult))
    props_update_j=json.dumps(props_update_d)

    if verbose:
        print >>sys.stderr, 'PUT', props_update_j, url
    if dryrun:
        return

    r=requests.put(url, data=props_update_j, headers={'content-type': 'application/json'})
    print r.status_code, r.content

@baker.command
def conflict_resolution_policy_doc():
    """show conflict resolution note
    Based on http://lists.basho.com/pipermail/riak-users_lists.basho.com/2011-November/006326.html
    """

    print "%-15s %-15s %-15s %s" % ('policy', 'last_write_wins', 'allow_mult', 'description')
    for name, (last_write_wins, allow_mult, desc) in conflict_resolution_policy_def.items():
        print "%-15s %-15s %-15s %s" % (name, str(last_write_wins), str(allow_mult), desc)


if __name__=='__main__':

    baker.run()
