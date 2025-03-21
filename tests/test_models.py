from src.core.models import OperationLog


def test_valid_operation_log_entry():
    log_data_dict = {
      "created_at": "2025-03-21 13:23:55",
      "updated_at": "2025-03-21 13:23:55",
      "user_id": "d7d880cea1844841ac1854f9140ba9a3",
      "user_name": "hww",
      "resource_type": "admin",
      "obj_id": "d7d880cea1844841ac1854f9140ba9a3",
      "obj_name": "hww",
      "ref_id": "",
      "ref_name": "",
      "status": "success",
      "request_ip": "10.52.17.91",
      "error_messages": "",
      "error_code": "",
      "operation_type": "business",
      "request_id": "c7e2810b-49aa-4463-9e25-4a29a5303072",
      "detail": {
        "resources": [
          {
            "id": "d7d880cea1844841ac1854f9140ba9a3",
            "name": "hww",
            "type": "admin"
          }
        ]
      },
      "action": "admin.login",
    }

    log_entry = OperationLog(**log_data_dict)