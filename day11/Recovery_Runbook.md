# Disaster Recovery Runbook: Вариант 5 (Маркетплейс «ВсёДляВсех»)
**Сценарий:** Полный отказ основного региона AWS (Frankfurt). Аварийное переключение и восстановление на резервной площадке GCP.

---

## Пошаговая инструкция для инженера дежурной смены (20 шагов)

### Фаза 1: Изоляция и перевод платформы в режим обслуживания (0 - 10 минут)
1. Проверить алерты в PagerDuty и зафиксировать недоступность API AWS Frankfurt.
2. Переключить глобальный трафик в Cloudflare на страницу-заглушку (Maintenance Page):
   ```bash
   cloudflare-cli dns update vsedlyavseh.ru --content 192.0.2.1 --ttl 60
   ```
3. Остановить входящие транзакции платежных шлюзов, отправив Webhook-сигнал отмены на ЮKassa/Stripe.
4. Активировать Telegram-бота технической поддержки для информирования продавцов и покупателей.

### Фаза 2: Развертывание резервного контура в GCP (10 - 40 минут)
5. Перекрестить терминал в каталог аварийной инфраструктуры: `cd /infra/terraform/gcp-dr-site`.
6. Запустить сборку сетевой архитектуры и нод в GCP:
   ```bash
   terraform init && terraform apply -auto-approve -var="env=disaster-recovery"
   ```
7. Убедиться в успешном старте инстансов: `gcloud compute instances list --filter="tags.list=dr-node"`.
8. Проверить сетевую связность (Ping/MTR) между новыми подами Kubernetes (GKE) и базами данных.

### Фаза 3: Восстановление Mission-Critical БД CockroachDB (40 - 90 минут)
9. Инициализировать пустой отказоустойчивый кластер CockroachDB в облаке GCP.
10. Запустить процедуру восстановления данных на момент времени (PITR) за 5 минут до аварии (14:25:00):
    ```bash
    cockroach backup restore orders \
    FROM 's3://vsedlyavseh-immutable-backups/cockroach/incremental?AWS_REGION=eu-central-1' \
    WITH AS OF SYSTEM TIME '2026-06-17 14:25:00+00:00';
    ```
11. Выполнить проверочный SQL-запрос для контроля целостности и консистентности структуры заказов:
    ```sql
    SELECT COUNT(*), SUM(order_total) FROM orders WHERE order_date = '2026-06-17';
    ```
12. Сверить полученную сумму с агрегатами из логов платежного шлюза.

### Фаза 4: Восстановление каталога товаров (Elasticsearch) (90 - 110 минут)
13. Подключить S3-репозиторий резервных копий к новому кластеру Elasticsearch в GCP:
    ```bash
    curl -X PUT "localhost:9200/_snapshot/gcp_dr_repo" -H 'Content-Type: application/json' -d'
    {"type": "s3", "settings": {"bucket": "vsedlyavseh-immutable-backups", "region": "eu-central-1", "base_path": "elasticsearch/snapshots"}}'
    ```
14. Запустить параллельное восстановление критичных поисковых индексов каталога:
    ```bash
    curl -X POST "localhost:9200/_snapshot/gcp_dr_repo/snapshot_latest/_restore" -H 'Content-Type: application/json' -d'
    {"indices": "catalog_products,catalog_vendors", "ignore_unavailable": true, "include_global_state": false}'
    ```
15. *Стратегия непрерывности покупок:* До окончания полной индексации Elasticsearch перенаправить запросы цен микросервиса `Catalog-Service` на чтение кэша из Redis Cluster. При поиске выдавать статический топ товаров.

### Фаза 5: Конфигурация брокера RabbitMQ и запуск платформы (110 - 120 минут)
16. Импортировать сохраненную топологию очередей и прав доступа RabbitMQ:
    ```bash
    rabbitmqadmin -H gcp-mq-node1.internal import /etc/rabbitmq/topology_backup.json
    ```
17. Увеличить количество реплик обработчиков (Consumers) в Kubernetes для разбора накопившихся очередей:
    ```bash
    kubectl scale deployment order-consumer-worker --replicas=50 -n production
    ```
18. Проверить работоспособность сквозных бизнес-сценариев: "Поиск -> Корзина -> Оплата".
19. Обновить DNS-записи в Cloudflare на балансировщик нагрузок GCP:
    ```bash
    cloudflare-cli dns update vsedlyavseh.ru --content gcp-gclb.vsedlyavseh.ru --ttl 60
    ```
20. Снять режим обслуживания и зафиксировать успешное восстановление платформы.