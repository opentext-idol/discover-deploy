#
# Copyright 2021-2024 Open Text.
#
# Licensed under the MIT License (the "License"); you may not use this file
# except in compliance with the License.
#
# The only warranties for products and services of Open Text and its affiliates
# and licensors ("Open Text") are as may be set forth in the express warranty
# statements accompanying such products and services. Nothing herein should be
# construed as constituting an additional warranty. Open Text shall not be
# liable for technical or editorial errors or omissions contained herein. The
# information contained herein is subject to change without notice.
#

ARG BASE_IMAGE
FROM $BASE_IMAGE

COPY custom/ /opt/nifi/nifi-current/extensions/

ENTRYPOINT ["/opt/nifi/nifi-current/scripts/start-nifi.sh"]
