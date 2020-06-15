#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Cloudera, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: jdbc_query
short_description: Query JDBC endpoints
description:
  - Execute statements to JDBC endpoints via the Java JDK and associated database JAR files.
author:
  - "Andre Araujo (@asdaraujo)"
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - jaydebeapi
seealso:
  - name: Package java.sql
    description: Provides the API for accessing and processing data stored in a data source (usually a relational database) using the Java programming language.
    link: https://docs.oracle.com/en/java/javase/20/docs/api/java.sql/java/sql/package-summary.html
notes:
  - I(check_mode) will suppress all interaction with the JDBC endpoint; all statements return an empty C(list).
  - Statements like C(INSERT) and C(INVALIDATE METADATA) which do not return results will throw an error when the module attempts to retrieve the result set. Use I(fail_on_none=False) to suppress this behavior.
options:
  url:
    description: JDBC endpoint URL
    required: True
    type: str
    aliases:
      - endpoint
      - connection_string
  class_name:
    description: Class name of the JDBC Driver
    type: str
    aliases:
      - classname
    default: com.cloudera.impala.jdbc.Driver
  driver_args:
    description:
      - Additional argument for the Driver.
      - See U(https://docs.oracle.com/en/java/javase/20/docs/api/java.sql/java/sql/DriverManager.htmlq) for details.
    type: dict
    aliases:
      - args
  jars:
    description:
      - JAR filename or sequence of filenames for the JDBC driver
      - The file(s) must be present on the target host.
      - Alternatively, provide the C(CLASSPATH) environment variable that includes the JAR(s).
    type: list
    elements: str
  libs:
    description:
      - DLL or SO filename or filenames of shared libraries used by the JDBC driver.
      - The file(s) must be present on the target host.
    type: list
    elements: str
    aliases:
      - libraries
  src:
    description:
      - Path to a query file (one or more statements separated by the I(query_delimiter)).
      - Can be absolute or relative, but the file must be present on the target host.
      - Mutually exclusive with I(content).
    type: path
    aliases:
      - query_file
      - file
  content:
    description:
      - String contents of a query (one or more statements separated by the I(query_delimiter)).
      - For advanced formatting or if I(content) contains a variable, use the M(ansible.builtin.template) module.
      - Mutually exclusive with I(src).
    type: str
    aliases:
      - query_text
      - text
  delimiter:
    description:
      - Query statement delimiter.
      - For each discrete statement, the statement is executed and its results returned.
    type: str
    required: False
    default: ';'
    aliases:
      - query_delimiter
  fail_on_error:
    description:
      - Flag to fail immediately for any statement that returns a JDBC error.
      - If set, statement processing will cease and an error raised.
      - Otherwise, the statement result will return an empty C(list).
    default: True
    type: bool
  fail_on_none:
    description:
      - Flag to fail immediately for any statement that does not return a valid result set.
      - If set, statement processing will cease and an error raised.
      - Otherwise, the statement result will return the result set.
    default: True
    type: bool
"""

# remote_src:
#   description:
#     - Influence whether I(src) needs to be transferred or already is present remotely.
#     - If C(false), it will search for I(src) on the controller node.
#     - If C(true) it will search for I(src) on the managed (remote) node.
#     - Autodecryption of files does not work when I(remote_src=yes).
#   type: bool
#   default: False

EXAMPLES = r"""
- name: Query a JDBC endpoint with two statements (with credentials as Driver arguments)
  cloudera.services.jdbc_query:
    endpoint: "jdbc:impala://some-host:20150/;"
    driver_args:
      UID: "your_username"
      PWD: "your_credentials"
    content: |
      SHOW TABLES IN your_database;
      SELECT COUNT(*) FROM your_database.the_table;
  environment:
    JAVA_HOME: "/some/path/to/java/home"
    CLASSPATH: "/classpath/here:/path/to/driver/jar/file"
  register: __results

- name: Query a JDBC endpoint with a file of query statements
  cloudera.services.jdbc_query:
    endpoint: "jdbc:impala://some-host:20150/;"
    file: file_with_statements.yml
  environment:
    JAVA_HOME: "/some/path/to/java/home"
    CLASSPATH: "/classpath/here:/path/to/driver/jar/file"
  register: __results

- name: Query a JDBC endpoint and do not stop processing on the Statement error.
  cloudera.services.jdbc_query:
    endpoint: "jdbc:impala://some-host:20150/;"
    content: |
      SHOW TABLES IN your_database;
      MALFORMED SQL STATEMENT;
      SELECT COUNT(*) FROM your_database.the_table;
    fail_on_error: no

- name: Query a JDBC endpoint and do not stop processing on the null result set.
  cloudera.services.jdbc_query:
    endpoint: "jdbc:impala://some-host:20150/;"
    content: "INSERT INTO my_table VALUES ('one','two','buckle','my','shoe')"
    fail_on_none: no
"""

RETURN = r"""
---
results:
  description:
    - Results from the JDBC query statements.
    - Each element of the returned list contains the output of each statement.
  returned: always
  type: list
  elements: list
"""

import jaydebeapi
import os

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.cloudera.services.plugins.module_utils.common import get_param


class JdbcQuery(AnsibleModule):
    def __init__(self, module):
        self.module = module

        self.url = get_param(module, "url")
        self.class_name = get_param(module, "class_name")
        self.driver_args = get_param(module, "driver_args")
        self.jars = get_param(module, "jars")
        self.libs = get_param(module, "libs")
        self.src = get_param(module, "src")
        self.content = get_param(module, "content")
        self.delimiter = get_param(module, "delimiter")
        self.fail_on_error = get_param(module, "fail_on_error")
        self.fail_on_none = get_param(module, "fail_on_none")

        # Initialize the return values
        self.changed = True
        self.stmt_results = []

    """Parse the query content into individual statements according to the delimiter."""

    def get_statements(self, content: str):
        if content is None:
            self.module.fail_json(msg="Query content is invalid.")

        # TODO Check if one can pass None as a module param to avoid the split
        if not self.delimiter:
            yield content
        else:
            # TODO Coordinate with stream processing to process large files/strings efficiently
            for split in [
                q.strip() for q in content.split(self.delimiter) if q.strip()
            ]:
                yield split

    def process(self):
        query = None

        # TODO Convert to read content and src via stream handlers
        # Read each handler up through the next delimiter and yield the found
        # statement - read() as chunks and then seek() for the next read() and
        # keep remainder until next read(). For example: https://stackoverflow.com/a/62638423
        # Currently, content and src are read completely into memory
        if self.content:
            query = self.content
        else:
            if not os.path.exists(self.src):
                self.module.fail_json(msg="Query file, %s, does not exist." % self.src)
            query = open(self.src, "r").read()  # TODO This does not close()

        try:
            with jaydebeapi.connect(
                self.class_name,
                self.url,
                self.driver_args,
                self.jars,
                self.libs,
            ) as conn:
                with conn.cursor() as curs:
                    for query in self.get_statements(query):
                        query_results = []

                        if not self.module.check_mode:
                            try:
                                curs.execute(query)
                            except jaydebeapi.Error as e:
                                if self.fail_on_error:
                                    self.module.fail_json(
                                        msg="Statement '%s' raised an error: %s"
                                        % (query, str(e)),
                                        error=to_native(e),
                                    )

                            try:
                                query_results = curs.fetchall()
                            except jaydebeapi.Error as e:
                                if self.fail_on_none:
                                    self.module.fail_json(
                                        msg="Statement '%s' returned None. If no result set is expected, you may "
                                        "avoid this error by setting 'fail_on_none=False'."
                                        % query,
                                    )

                        self.stmt_results.append(query_results)
        except Exception as e:
            self.module.fail_json(
                msg="Unable to establish connection or cursor: %s" % str(e),
            )


def main():
    module = AnsibleModule(
        argument_spec=dict(
            url=dict(
                required=True,
                aliases=["endpoint", "connection_string"],
                no_log=True,
            ),
            class_name=dict(
                aliases=["classname"],
                default="com.cloudera.impala.jdbc.Driver",
            ),
            driver_args=dict(type="dict", aliases=["args"], no_log=True),
            jars=dict(type="list", elements="str"),
            libs=dict(aliases=["libraries"]),
            src=dict(type="path", aliases=["query_file", "file"]),
            content=dict(aliases=["query_text", "text"]),
            delimiter=dict(aliases=["query_delimiter"], default=";"),
            fail_on_error=dict(type="bool", default=True),
            fail_on_none=dict(type="bool", default=True),
        ),
        required_one_of=[
            ["src", "content"],
        ],
        supports_check_mode=True,
    )

    result = JdbcQuery(module)
    result.process()

    output = dict(
        changed=result.changed,
        results=result.stmt_results,
    )

    module.exit_json(**output)


if __name__ == "__main__":
    main()
