def vehicleslam(vehicles):
    stack = []
    for vehicle in vehicles:
        while stack and vehicle < 0 < stack[-1]:  # Collision condition
            if abs(vehicle) > abs(stack[-1]):  # Current vehicle is faster
                stack.pop()  # Remove the last vehicle
                continue  # Check the current vehicle again
            elif abs(vehicle) == abs(stack[-1]):  # Same speed
                stack.pop()  # Both vehicles are removed
            break  # No more collisions possible
        else:
            stack.append(vehicle)  # No collision, add vehicle to stack
    return stack

ls = [3,-2,0,4]
a = vehicleslam(ls)
print(a)