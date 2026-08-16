from pydantic import BaseModel, conint, conlist, model_validator


class CreateSimulation(BaseModel):
    nr_simulations: int
    backlog_min: int
    backlog_max: int
    capacity: int
    throughput: list[int]

    @model_validator(mode="after")
    def check_nr_simulations(self) -> 'CreateSimulation':
        if (self.nr_simulations < 100 or self.nr_simulations > 10000) :
            raise ValueError('O número de simulações é inválido. O número de simulações deve ser entre 100 a 10.000 simulações.')
        return self

    @model_validator(mode="after")
    def check_backlog_min(self) -> 'CreateSimulation':
        if self.backlog_min <= 0:
            raise ValueError('o backlog mínimo deve ser maior que 0.')
        return self


    @model_validator(mode="after")
    def check_backlog_max(self) -> 'CreateSimulation':
        if self.backlog_max < self.backlog_min:
            raise ValueError('o backlog máximo deve ser igual ou maior que o backlog mínimo')
        return self
    @model_validator(mode="after")
    def check_capacity(self) -> 'CreateSimulation':
        if not self.capacity or self.capacity < 10 or self.capacity > 100:
            raise ValueError('Preencha o Capacity com um valor entre 10% a 100% .')
        return self
    
    @model_validator(mode="after")
    def check_throughput(self) -> 'CreateSimulation':
        if not self.throughput or len(self.throughput) < 4:
            raise ValueError('O throughput mínimo deve ser de 4 semanas.')
        return self