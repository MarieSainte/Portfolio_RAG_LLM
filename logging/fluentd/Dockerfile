# Fluentd + plugin de sortie Loki (grafana/loki).
FROM fluent/fluentd:v1.16-debian-1

USER root
RUN gem install fluent-plugin-grafana-loki --version '~> 1.2' --no-document
USER fluent
