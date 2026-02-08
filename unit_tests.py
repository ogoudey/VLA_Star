import gda


import asyncio
import vla_complex
import time
l = gda.OrderedContextLLMAgent("tester", "hi", "g")

a = vla_complex.UnityArm("arm")
b = vla_complex.UnityDrive("drive")
c = vla_complex.Chat("chat")
l.link_vla_complexes([a, b, c])
b.state.add_to_session("status", "driving to store")
time.sleep(1)
b.state.add_to_session("status", "arrived at store")
time.sleep(1)
a.state.add_to_session("status", "picked up breakfast")
time.sleep(1)
c.state.add_to_session("message", "hello robot")
l.context_init()
print(l.context)

l.order_context()
print(l.ordered_context)
print("--------------------------------\n\n\n")
sc = asyncio.run(l.summarize_states())
l.update_states_with_summarization(sc)
l.context_init()
print(l.context)

l.order_context()
print(l.ordered_context)
print("--------------------------------\n\n\n")