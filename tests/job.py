from linkedin import linkedin_jobs
from programathor import thor_jobs


thor=  thor_jobs(search='Júnior')
output= []
for job in thor:
    techs_str = ", ".join(job["Techs"])

    output.append(f'\nJob: {job["Job"]}\nApply: {job["Apply"]}\nTechs: {techs_str}')

result = "\n".join(output)


linked = linkedin_jobs(search='junior',cd=True)
resultado = []
for job in linked :
    resultado.append(f'\nJob: {job["Job"]}\nApply: {job["Apply"]}')
resultt = "\n".join(resultado)


print(result)
print(resultt)

print(type(resultt))
print(type(result))
