#!/bin/bash
if test $(ssh connectit.ubs.dev "(timeout 1s tail -f -n0 /var/log/autopilot/connectit/connect-incident-rest-api.log | fgrep -c 'kafka.producer.SyncProducer:Connected to localhost:9099 for producing') 2>/dev/null") -gt 2
then
  echo "alarm"
  aae_putissue -u tcp://localhost:7284 <(cat <<end-of-issue
Issue:
  IssueSubject: ConnectIT not working
  NodeID: mklemmarago.de:mklemmarago.de:Machine:DefaultIssueNode
  xmlns: https://graphit.co/schemas/v2/IssueSchema
  ticket_sourceStatus:
    Content:
      Value: New
      CreatedOn: mklemmarago.de:mklemmarago.de:Machine:DefaultIssueNode
end-of-issue)
else
  echo "alles klar"
fi
