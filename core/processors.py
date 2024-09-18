import csv
import logging
import re
from decimal import Decimal
from typing import IO, Literal, Callable

from core.models import Department, District, Locality, Establishment, Institution

logger = logging.getLogger(__name__)


class DataImporter:
    def __init__(
        self, file: IO, import_type: Literal["establishments", "institutions"]
    ):
        super().__init__()
        self.import_type = import_type
        self.departments = {}
        self.districts = {}
        self.localities = {}
        self.establishments = {}
        self.reader = csv.DictReader(file)
        self.skipped_rows = []

    def process(self):
        logger.info(f"Processing file containing {self.import_type}")
        idx = 0
        processor: Callable = (
            self.process_establishments_row
            if self.import_type == "establishments"
            else self.process_institutions_row
        )
        for idx, row in enumerate(self.reader):
            processor(row, idx)
        logger.info(
            f"Finished processing {idx + 1} rows. Skipped {len(self.skipped_rows)} rows."
        )
        return self.skipped_rows

    def process_establishments_row(self, row, idx: int):
        department = self._get_department(row)
        if not department:
            self.skipped_rows.append((idx + 2, "Falta código departamento"))
            return
        district = self._get_district(row)
        if not district:
            self.skipped_rows.append((idx + 2, "Falta código distrito"))
            return
        locality = self._get_locality(row)
        if not locality:
            self.skipped_rows.append((idx + 2, "Falta código barrio/localidad"))
            return
        establishment = self._get_establishment(row)
        if not establishment:
            self.skipped_rows.append((idx + 2, "Falta código establecimiento"))
            return
        return establishment

    def process_institutions_row(self, row, idx: int):
        code = row.get("codigo_establecimiento")
        if not code:
            self.skipped_rows.append((idx + 2, "Falta código establecimiento"))
        try:
            if code not in self.establishments:
                self.establishments[code] = Establishment.objects.get(code=code)
        except Establishment.DoesNotExist:
            establishment = self.process_establishments_row(row, idx)
            if not establishment:
                return
            self.establishments[code] = establishment
        try:
            institution = self._get_institution(row, self.establishments[code])
        except ValueError as exc:
            self.skipped_rows.append((idx + 2, str(exc)))
            return
        return institution

    def _get_department(self, row):
        code = row.get("codigo_departamento")
        if not code:
            return
        if len(code) < 2:
            code = f"0{code}"
        if code not in self.departments:
            self.departments[code], _ = Department.objects.update_or_create(
                code=code, defaults={"name": row.get("nombre_departamento", "")}
            )
        return self.departments[code]

    def _get_district(self, row):
        department = self._get_department(row)
        code = row.get("codigo_distrito")
        if not department or not code:
            return
        key = f"{department.code}-{code}"
        if key not in self.districts:
            self.districts[key], _ = District.objects.update_or_create(
                code=code,
                department=department,
                defaults={
                    "name": row.get("nombre_distrito", ""),
                },
            )
        return self.districts[key]

    def _get_locality(self, row):
        district = self._get_district(row)
        code = row.get("codigo_barrio_localidad")
        if not district or not code:
            return
        key = f"{district.department.code}-{district.code}-{code}"
        if key not in self.localities:
            self.localities[key], _ = Locality.objects.update_or_create(
                code=code,
                district=district,
                defaults={
                    "name": row.get("nombre_barrio_localidad", ""),
                },
            )
        return self.localities[key]

    def _get_establishment(self, row):
        code = row.get("codigo_establecimiento")
        if not code:
            return
        if code not in self.establishments:
            self.establishments[code], _ = Establishment.objects.update_or_create(
                code=code,
                defaults={
                    "last_data_capture": row.get("anio"),
                    "district": self._get_district(row),
                    "locality": self._get_locality(row),
                    "zone_code": row.get("codigo_zona", ""),
                    "zone_name": row.get("nombre_zona", ""),
                    "address": row.get("direccion", ""),
                    "latitude": self.convert_coordinate(row.get("latitud", "")),
                    "longitude": self.convert_coordinate(row.get("longitud", "")),
                },
            )
        return self.establishments[code]

    @staticmethod
    def _get_institution(row, establishment: Establishment):
        code = row.get("codigo_institucion").replace(".", "").replace(" ", "")
        if not code:
            raise ValueError("Falta código institución")
        try:
            code = abs(int(code))
        except ValueError:
            raise ValueError("Código inválido")

        institution, _ = Institution.objects.update_or_create(
            code=code,
            establishment=establishment,
            name=row.get("nombre_institucion", ""),
            defaults={
                "institution_type": row.get("sector_o_tipo_gestion", "DESCONOCIDO"),
                "phone_number": row.get("nro_telefono", ""),
                "website": row.get("paginaweb", ""),
                "email": row.get("email", ""),
            },
        )
        return institution

    @staticmethod
    def convert_coordinate(deg_coord: str):
        """Converts coordinates in Deg, min secs to decimal"""

        if not deg_coord:
            return
        try:
            deg, minutes, seconds, direction = re.split("[º'\"]", deg_coord)
        except ValueError:
            return
        deg = deg.replace(" ", "")
        minutes = minutes.replace(" ", "")
        seconds = seconds.replace(" ", "")
        direction = direction.upper().replace(" ", "")
        try:
            return Decimal(
                (float(deg) + float(minutes) / 60 + float(seconds) / (60 * 60))
                * (-1 if direction in ["W", "S"] else 1)
            )
        except ValueError:
            return
