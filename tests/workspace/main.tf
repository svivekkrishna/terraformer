
resource "random_string" "first" {
  length = 16
}

resource "null_resource" "first" {
  triggers = {
    id = "${random_string.first.id}"
  }
}


resource "random_string" "second" {
  length = 16
}

resource "null_resource" "second" {
  triggers = {
    id = "${random_string.second.id}"
  }
}


resource "random_string" "third" {
  length = 16
}

resource "null_resource" "third" {
  triggers = {
    id = "${random_string.third.id}"
  }
}
