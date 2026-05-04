from dataclasses import dataclass


INFINITE = "∞"


@dataclass(frozen=True)
class KendallNotation:
    arrival_process: str = "M"
    service_distribution: str = "G"
    servers: int | str = "c"
    queue_capacity: int | str = INFINITE
    population: int | str = INFINITE
    discipline: str = "FIFO"

    def as_string(self) -> str:
        return (
            f"{self.arrival_process}/"
            f"{self.service_distribution}/"
            f"{self.servers}/"
            f"{self.queue_capacity}/"
            f"{self.population}/"
            f"{self.discipline}"
        )

    def __str__(self) -> str:
        return self.as_string()


def kendall_notation(
    arrival_process: str = "M",
    service_distribution: str = "G",
    servers: int | str = "c",
    queue_capacity: int | str = INFINITE,
    population: int | str = INFINITE,
    discipline: str = "FIFO",
) -> str:
    return KendallNotation(
        arrival_process=arrival_process,
        service_distribution=service_distribution,
        servers=servers,
        queue_capacity=queue_capacity,
        population=population,
        discipline=discipline,
    ).as_string()


if __name__ == "__main__":
    print(KendallNotation())
