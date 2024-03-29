import re

greek_letters = ["alpha", "beta", "gamma", "delta", "epsilon", "theta", "iota",
                 "kappa", "lambda", "mu", "nu", "pi", "rho", "sigma", "phi", "psi", "omega",\
                 "cos", "sin", "tan", "sec", "cosec", "cot"]


def parse_one(equation, debug=False):
    """This method converts one equation given in string into tex string
    Args:
        equation (string): string of the neurodiffeq code for the differential equation 
    Returns:
        string: tex string which can be used for rendering in the frontend
    """
    
    equation = equation.replace('[', '')
    equation = equation.replace(']', '')
    equation = equation.replace('torch.', '')
    equation = equation.replace('np.', '')
    equation = equation.replace('exp', '{\\rm e}^')
    equation = equation.replace('_', '\_')
    
    # Get the individual terms
    open = 0
    close = 0
    start_index = 0
    stop_index = 0
    terms = []
    for i in range(len(equation)):
        if equation[i] == '(':
            open += 1
        elif equation[i] == ')':
            close += 1
        elif equation[i] == '+' or equation[i] == '-':
            if open == close:
                stop_index = i
                terms.append(equation[start_index:stop_index].strip())
                start_index = i+1
                terms.append(equation[i])

    terms.append(equation[start_index:len(equation)].strip())
    if debug:
        print("terms are:")
        print(terms)
    
    #Testing to find factors of terms
    #print("Finding Parameters:")
    params = []
    signs = []
    for t in terms:
        if (t!="+" and t!="-"):
            #print(t)
            if "diff" in t:
                t = t.strip(")")
                t = t.strip("(")
                #print(t)
                diff_loc = t.find("diff")
                #print(diff_loc)
                if(diff_loc==0):
                    params.append(1.0)
                else:
                    num_param = ""
                    for ti in t:
                        if(ti=="*"):
                            break
                        else:
                            num_param+=ti
                    if(num_param.isalpha()):
                      #print(num_param)
                      params.append(1.0)
                    else:
                      params.append(float(num_param))
            else: #Normal term
                t = t.strip(")")
                t = t.strip("(")
                #print(t)
                if(t[0].isnumeric()):
                    num_param = ""
                    for ti in t:
                        if(ti=="*"):
                            break
                        else:
                            num_param+=ti
                    if(num_param.isalpha()):
                      #print(num_param)
                      params.append(1.0)
                    else:
                      params.append(float(num_param))
                else:
                    params.append(1.0)
        else:
            signs.append(t)
    final_params = [params[0]]
    for sign, param in zip(signs, params[1:]):
        if sign=="-":
            final_params.append(-1*param)
        else:
            final_params.append(param)

    #print("Parameters are:")
    #print(final_params)
    

    # Get independent variables
    independent_variables = []
    for i in terms:
        diff_index = i.find('diff')
        if diff_index != -1:
            number_terms = i.split(',')
            if debug:
                print("Number of terms split by ,:")
                print(number_terms)
            if len(number_terms) == 2:
                independent_variables.append(i.strip()[-2])
            elif len(number_terms) == 3:
                independent_variables.append(number_terms[1].strip()[-1])

    if debug:
        print("Independent Variables:")
        print(independent_variables)
    independent_variables = list(set(independent_variables))

    # PDEs: 1, ODEs: 0
    opde = 1 if len(independent_variables) > 1 else 0

    tex = ''
    re_int = re.compile(r'\b\d+\b')

    # PDEs
    if opde == 1:
        for i in terms:

            i = i.replace('**', '^')
            list_i = list(i)
            #print(list_i)
            final_m = [(m.start(0), m.end(0)) for m in re.finditer(r'\^', i)]
            for match_span in final_m:
              if(i[match_span[1]]=="("):
                #print(match_span[1])
                list_i[match_span[1]] = "{("
                open_cnt = 1
                close_cnt = 0
                for ind in range(match_span[1]+1, len(i)):
                  if(i[ind]=="("):
                    open_cnt+=1
                  elif(i[ind]==")"):
                    close_cnt+=1
                  
                  if(open_cnt==close_cnt):
                    #print("Closing Location is: ", ind)
                    #print(i[ind])
                    list_i[ind] = ")}"
                    break
            #print(i)      
            #print(''.join(list_i))
            i = ''.join(list_i)
            #print(final_m)
            #i = i.replace('*', '')

            # Replacing for / division with frac
            list_i = list(i)
            final_m = [(m.start(0), m.end(0)) for m in re.finditer(r'/', i)]
            #print("Division: ",final_m)
            for match_span in final_m:
              
              if(i[match_span[1]]=="("):
                #print(match_span[1])
                list_i[match_span[1]] = "{("
                open_cnt = 1
                close_cnt = 0
                for ind in range(match_span[1]+1, len(i)):
                  if(i[ind]=="("):
                    open_cnt+=1
                  elif(i[ind]==")"):
                    close_cnt+=1
                  
                  if(open_cnt==close_cnt):
                    #print("Closing Location is: ", ind)
                    #print(i[ind])
                    list_i[ind] = ")}"
                    break
              else:
                list_i[match_span[1]]= "{" +list_i[match_span[1]] + "}"

              if(i[match_span[0]-1]==")"):
                list_i[match_span[0]-1] = ")}"
                open_cnt = 1
                close_cnt = 0
                for ind in range(match_span[0]-2, 0, -1):
                  if(i[ind]==")"):
                    open_cnt+=1
                  elif(i[ind]=="("):
                    close_cnt+=1
                  
                  if(open_cnt==close_cnt):
                    #print("Closing Location is: ", ind)
                    #print(i[ind])
                    list_i[ind] = "\\frac{("
                    break
              else:
                list_i[match_span[0]-1] = "\\frac{" + list_i[match_span[0]-1] + "}"

              list_i[match_span[0]]=""
              #print("Division :", list_i)

            #print("New List:", list_i)
            i = ''.join(list_i)
            #print("i is:",i)
            i = i.replace('*', '\\ ')
            #print("i * replaced is:",i)
            diff_index = i.find('diff')
            if diff_index != -1:
                pre_term = i[:diff_index]
                pre_term = pre_term.strip("(")
                tex += pre_term.strip()
                tex += " "
                term = i[diff_index:]
                term_inside = term[5:]
                number_terms = term_inside.split(',')
                if len(number_terms) == 3: 
                    order = re_int.findall(number_terms[2])[0]
                    if order != '1':
                        tex += r'\frac{\partial^' + order + \
                            number_terms[0] + r'}{\partial ' + number_terms[1] + '^' + order + '}'
                    else:
                        tex += r'\frac{\partial ' + number_terms[0] + \
                        r'}{\partial ' + number_terms[1].strip()[0] + '}'
                else:
                    tex += r'\frac{\partial ' + number_terms[0] + \
                        r'}{\partial ' + number_terms[1].strip()[0] + '}'
            else:
                tex += i

    # ODEs
    elif opde == 0:
        for i in terms:

            i = i.replace('**', '^')
            list_i = list(i)
            #print(list_i)
            final_m = [(m.start(0), m.end(0)) for m in re.finditer(r'\^', i)]
            for match_span in final_m:
              if(i[match_span[1]]=="("):
                #print(match_span[1])
                list_i[match_span[1]] = "{("
                open_cnt = 1
                close_cnt = 0
                for ind in range(match_span[1]+1, len(i)):
                  if(i[ind]=="("):
                    open_cnt+=1
                  elif(i[ind]==")"):
                    close_cnt+=1
                  
                  if(open_cnt==close_cnt):
                    #print("Closing Location is: ", ind)
                    #print(i[ind])
                    list_i[ind] = ")}"
                    break
            #print(i)      
            #print(''.join(list_i))
            i = ''.join(list_i)
            #print(final_m)
            #i = i.replace('*', '')

            # Replacing for / division with frac
            list_i = list(i)
            final_m = [(m.start(0), m.end(0)) for m in re.finditer(r'/', i)]
            #print("Division: ",final_m)
            for match_span in final_m:
              
              if(i[match_span[1]]=="("):
                #print(match_span[1])
                list_i[match_span[1]] = "{("
                open_cnt = 1
                close_cnt = 0
                for ind in range(match_span[1]+1, len(i)):
                  if(i[ind]=="("):
                    open_cnt+=1
                  elif(i[ind]==")"):
                    close_cnt+=1
                  
                  if(open_cnt==close_cnt):
                    #print("Closing Location is: ", ind)
                    #print(i[ind])
                    list_i[ind] = ")}"
                    break
              else:
                list_i[match_span[1]]= "{" +list_i[match_span[1]] + "}"

              if(i[match_span[0]-1]==")"):
                list_i[match_span[0]-1] = ")}"
                open_cnt = 1
                close_cnt = 0
                for ind in range(match_span[0]-2, 0, -1):
                  if(i[ind]==")"):
                    open_cnt+=1
                  elif(i[ind]=="("):
                    close_cnt+=1
                  
                  if(open_cnt==close_cnt):
                    #print("Closing Location is: ", ind)
                    #print(i[ind])
                    list_i[ind] = "\\frac{("
                    break
              else:
                list_i[match_span[0]-1] = "\\frac{" + list_i[match_span[0]-1] + "}"

              list_i[match_span[0]]=""
              #print("Division :", list_i)

            #print("New List:", list_i)
            i = ''.join(list_i)
            #print("i is:", i)
            i = i.replace('*', '\\ ')
            #print("i * is:", i)

            diff_index = i.find('diff')
            if diff_index != -1:
                pre_term = i[:diff_index]
                #print("pre-term:", pre_term)
                pre_term = pre_term.strip("(")
                tex += pre_term.strip() 
                tex += " "
                #print("tex is now:", tex)
                term = i[diff_index:]
                #print("term:", term)
                term_inside = term[5:]
                #print("term inside:", term_inside)
                number_terms = term_inside.split(',')
                if len(number_terms) == 3:#This means there is an 'order=' term present
                    order = re_int.findall(number_terms[2])[0]
                    if order != '1':
                        tex += r'\frac{d^' + order + \
                            number_terms[0] + '}{d ' + number_terms[1] + '^' + order + '}'
                    else:
                        tex += r'\frac{d ' + number_terms[0] + '}{d ' + \
                            number_terms[1].strip()[0] + '}'
                else:
                    tex += r'\frac{d ' + number_terms[0] + '}{d ' + \
                        number_terms[1].strip()[0] + '}'
            else:
                tex += i
    
    # = 0 to complete the equation
    tex = tex + " = 0"
    
    return tex


def parse_string(equation_string, debug=False):
    """This method parses multiple equations in the string
    Args:
        equation_string (string): This is of the form "[eq1, eq2, eq3, ...]" or "lambda x,y,z: [eq1, eq2, eq3, ...]" 
                                                   or "lambda x,y,z: eq"     or "eq".
    Returns:
        parsed_equations: List of parsed equations in tex strings
    """

    string = equation_string
    
    lambda_colon = string.find(':')
    if lambda_colon != -1:
        string = string[lambda_colon+1:]
        
    starting_bracket = string.find('[')
    if starting_bracket != -1:
        string = string[starting_bracket:]
    

    equations_string_list = []
    open = 0
    close = 0
    start_index = 0
    stop_index = 0

    string = string.replace('[', '')
    string = string.replace(']', '')

# This loop is to parse and finds the different equations in the given string
# If more than 1 equation present (Example in a System of Equations)
    for i in range(len(string)):
        if string[i] == '(':
            open += 1
        elif string[i] == ')':
            close += 1
        elif string[i] == ',':
            if open == close:
                stop_index = i
                equations_string_list.append(string[start_index:stop_index].strip())
                start_index = i + 1
#In Case we find more than one equation, means that the left over part after the last, will be blank (after stripping), so ignored
#In Case there was only 1 equation, then entire string stripped of spaces from both side fed in as an equation
    if string[start_index:len(string)].strip() != '': 
        equations_string_list.append(string[start_index:len(string)].strip())

    if debug:
        print("Equation List is:")
        print(equations_string_list)
    parsed_equations = []
    
    for eq in equations_string_list:
        p_e = parse_one(eq, debug)
          
        for g in greek_letters:
            p_e = p_e.replace(g, '\\' + g + ' ')
        
        parsed_equations.append(p_e)

    #print(parsed_equations)

    return parsed_equations


def parse_conditions(conditions, independent_variables, dependent_variables):
    parsed_conditions = []

    if (conditions is not None and dependent_variables is not None and independent_variables is not None):
        for i in range(len(conditions)):
            if conditions[i]['condition_type'] == 'DirichletBVP2D':
                cond_1 = conditions[i]['f0']
                cond_2 = conditions[i]['f1']
                cond_3 = conditions[i]['g0']
                cond_4 = conditions[i]['g1']

                cond_1 = cond_1.split(',')
                x_min = cond_1[0][-1]
                cond_1_arg = cond_1[1].split(':')[1].strip()
                cond_1_arg = cond_1_arg.replace('torch.', '')
                cond_1_arg = cond_1_arg.replace('np.', '')
                cond_1 = dependent_variables[0] + '(' + x_min + ', ' + \
                    independent_variables[1] + ') = ' + cond_1_arg
                #print(cond_1)

                cond_2 = cond_2.split(',')
                x_max = cond_2[0][-1]
                cond_2_arg = cond_2[1].split(':')[1].strip()
                cond_2_arg = cond_2_arg.replace('torch.', '')
                cond_2_arg = cond_2_arg.replace('np.', '')
                cond_2 = dependent_variables[0] + '(' + x_max + ', ' + \
                    independent_variables[1] + ') = ' + cond_2_arg
                #print(cond_2)

                cond_3 = cond_3.split(',')
                y_min = cond_3[0][-1]
                cond_3_arg = cond_3[1].split(':')[1].strip()
                cond_3_arg = cond_3_arg.replace('torch.', '')
                cond_3_arg = cond_3_arg.replace('np.', '')
                cond_3 = dependent_variables[0] + '(' + y_min + ', ' + \
                    independent_variables[0] + ') = ' + cond_3_arg
                #print(cond_3)

                cond_4 = cond_4.split(',')
                y_max = cond_4[0][-1]
                cond_4_arg = cond_4[1].split(':')[1].strip()
                cond_4_arg = cond_4_arg.replace('torch.', '')
                cond_4_arg = cond_4_arg.replace('np.', '')
                cond_4 = dependent_variables[0] + '(' + y_max + ', ' + \
                    independent_variables[0] + ') = ' + cond_4_arg
                #print(cond_4)

                parsed_conditions.append(cond_1)
                parsed_conditions.append(cond_2)
                parsed_conditions.append(cond_3)
                parsed_conditions.append(cond_4)

            elif conditions[i]['condition_type'] == 'IVP':

                if len(dependent_variables) > 1:
                    if conditions[i]['u_0'] is not None:
                        parsed_conditions.append(
                            str(dependent_variables[i]) + '(' + str(conditions[i]
                                                                    ['t_0']) + ') = ' + str(conditions[i]['u_0']))

                    if conditions[i]['u_0_prime'] is not None:
                        parsed_conditions.append(
                            r'\frac{d ' + str(dependent_variables[i]) + '}{d' + str(independent_variables[0]) +
                            '}(' + str(conditions[i]['t_0']) +
                            ') = ' + str(conditions[i]['u_0_prime']))

                else:
                    if conditions[i]['u_0'] is not None:
                        parsed_conditions.append(
                            str(dependent_variables[0]) + '(' + str(conditions[i]
                                                                    ['t_0']) + ') = ' + str(conditions[i]['u_0']))

                    if conditions[i]['u_0_prime'] is not None:
                        parsed_conditions.append(
                            r'\frac{d ' + str(dependent_variables[0]) + '}{d' + str(independent_variables[0]) +
                            '}(' + str(conditions[i]['t_0']) +
                            ') = ' + str(conditions[i]['u_0_prime']))

        for i in range(len(parsed_conditions)):
            parsed_conditions[i] = parsed_conditions[i].replace('**', '^')
            parsed_conditions[i] = parsed_conditions[i].replace('*', '')
            for g in greek_letters:
                parsed_conditions[i] = parsed_conditions[i].replace(
                    g, '\\' + g + ' ')

        #print(parsed_conditions)

    return parsed_conditions



# parse_string(
#     '[ diff(u, t) - (alpha*u  - beta*u*v),diff(v, t) - (delta*u*v - gamma*v), ]')
# parse_string(
#     '[diff(p, t) + diff(p*(a*x - b*x**3) + 2, x) - (s**2/2)*diff(p, x, order=2)]')

# parse_conditions([{
#     'condition_type': "DirichletBVP2D",
#     'f0': "x_min=0, x_min_val=lambda y: torch.sin(np.pi*y)",
#     'f1': "x_max=1, x_max_val=lambda y: 0,",
#     'g0': "y_min=0, y_min_val=lambda x: 0,",
#     'g1': "y_max=1, y_max_val=lambda x: 0,",
#     'x0': 0,
#     'x1': 1,
#     'y0': 0,
#     'y1': 1
# }], ['x', 'y'], ['u'])
