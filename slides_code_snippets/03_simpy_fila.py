def run_fifo_simulation(lambda_hora, c, service_stats, seed):
    rng = random.Random(seed)
    env = simpy.Environment()
    resource = simpy.Resource(env, capacity=c)
    waits, system_times = [], []
    arrival_process = ArrivalProcess(lambda_hora, rng)
    service_sampler = ServiceTimeSampler("deterministic", service_stats, rng)

    def handle_request(arrival_time):
        with resource.request() as request:
            yield request
            service_start = env.now
            wait_time = service_start - arrival_time
            service_time = service_sampler.sample_seconds()
            yield env.timeout(service_time)
            service_end = env.now
            waits.append(wait_time)
            system_times.append(service_end - arrival_time)

    def generate_arrivals():
        while env.now < SIMULATION_DURATION_SECONDS:
            yield env.timeout(arrival_process.next_interarrival_seconds())
            env.process(handle_request(env.now))
