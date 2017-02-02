#!/bin/bash
CONFIGFILE="/opt/autopilot/conf/aae.yaml"

SCRIPTNAME=$(basename $0)
SCRIPTDIR=$(cd -P $(dirname $0) && pwd)
EXIT_SUCCESS=0
EXIT_FAILURE=1
EXIT_ERROR=2
EXIT_FATAL=10

function usage {
  echo "Usage: $SCRIPTNAME -o <owner> <form_name> ..." >&2

  [[ $# -eq 1 ]] && exit $1 || exit $EXIT_FAILURE
}

while getopts ':o:h' OPTION; do
    case $OPTION in
        h) usage $EXIT_SUCCESS
           ;;
        o) OWNER="$OPTARG"
           ;;
        \?) echo "Unknown option \"-$OPTARG\"." >&2
            usage $EXIT_ERROR
            ;;
        :) echo "Option \"-$OPTARG\" needs an argument." >&2
           usage $EXIT_ERROR
           ;;
        *) echo "This shouldn't happen ..." >&2
           usage $EXIT_FATAL
           ;;
    esac
done

if [[ -z "$OWNER" ]]
then
  (>&2 echo "No owner specified!")
  exit 5 
fi

shift $(( OPTIND -1 ))

parse_yaml() {
local prefix=$2
local s
local w
local fs
    s='[[:space:]]*'
    w='[a-zA-Z0-9_]*'
    fs="$(echo @|tr @ '\034')"
    sed -ne "s|^\($s\)\($w\)$s:$s\"\(.*\)\"$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s[:-]$s\(.*\)$s\$|\1$fs\2$fs\3|p" "$1" |
    awk -F"$fs" '{
    indent = length($1)/2;
    vname[indent] = $2;
    for (i in vname) {if (i > indent) {delete vname[i]}}
        if (length($3) > 0) {
            vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
            printf("%s%s%s=(\"%s\")\n", "'"$prefix"'",vn, $2, $3);
        }
    }' | sed 's/_=/+=/g'
}

CONFIG=$(parse_yaml $CONFIGFILE)
eval $(fgrep Authentication_UserInputClientID <<< "$CONFIG")
eval $(fgrep Authentication_UserInputClientSecret <<< "$CONFIG")
eval $(fgrep Authentication_URL <<< "$CONFIG")
eval $(fgrep SyncHandler_URL <<< "$CONFIG")

for VALUE in SyncHandler_URL Authentication_UserInputClientID Authentication_UserInputClientSecret Authentication_URL
do if [[ -z "${!VALUE}" ]]
then
  (>&2 echo "$VALUE not set in $CONFIGFILE")
  exit 5
fi done

TOKEN=$(curl -s -u $Authentication_UserInputClientID:$Authentication_UserInputClientSecret -k -d "grant_type=client_credentials&scope=syncer,openid" -H "Content-Type:application/x-www-form-urlencoded" $Authentication_URL/oauth2/token | python -c "import sys, json; print json.load(sys.stdin)['access_token']")

for FORMNAME in "$@"
do
  QUERY="ogit\/_type:\"ogit\/Task\" AND ogit\/status:\"TEMPLATE\" AND ogit\/name:\"$FORMNAME\""
  VERTEX=$(curl -s -k -X GET -H "_TOKEN:$TOKEN" -H "Content-Type: application/json" -G --data-urlencode "query=$QUERY" "$SyncHandler_URL/query/vertices" | python -c "import sys, json; print json.load(sys.stdin)['items'][0]['ogit/_id']" 2>/dev/null)
  if [[ -z "$VERTEX" ]]
  then
    (>&2 echo "No task template with name \"$FORMNAME\" found.")
  else
    echo -n "Setting owner of vertex \"$VERTEX\" to \"$OWNER\" ... "
    OUTPUT=$(curl -s -k -X POST -sw '\n%{http_code}' -d "{\"ogit/_owner\": \"$OWNER\"}" -H "_TOKEN: $TOKEN" "$SyncHandler_URL/$VERTEX")
    STATUS=$(tail -n1 <<< "$OUTPUT")
    MSG=$(head -n -1 <<< "$OUTPUT")
    if [[ "$STATUS" == "200" ]]
    then
      echo okay.
    else
      echo "failed: $(echo $MSG | python -c "import sys, json; print json.load(sys.stdin)['error']['message']")."
    fi
  fi
done





