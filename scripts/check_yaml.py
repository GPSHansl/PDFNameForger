import yaml

data = yaml.safe_load(open('/app/config/sim.de.yml'))
print("Raw YAML variables:")
for i, var in enumerate(data.get('variables', []), 1):
    print(f"{i}. {var['name']}: format_spec={var.get('format_spec')}")
